#!/bin/python
from collections import OrderedDict
import re

def build_tree(dataset, depth_current, lines):  #build the dataset
    while len(lines) > 0:
        line = lines[0]
        depth = len(line) - len(line.lstrip())    #get number of spaces at head of line
        if depth < depth_current:    #depth change ends the current funtion
            return    #return to the previos depth
#        print('C Depth:', depth_current, 'L Depth:', depth, '-', line)
#        line = line.lstrip()    #clear the spaces at begining of line allowing for spaing to change without reporting
            # this creats the headache of determineing how to restore the original formatting.
        if line.startswith('! ') or line.lstrip() == '!':    #filtering comments in the set
            lines.pop(0)
        elif line.startswith('banner'):    #banners dont indent the same as other sections
            l = []
            header = line
            dataset[header] = OrderedDict()    #add to the tree
            dataset[header]['header'] = depth_current
            lines.pop(0)
            while (line != 'EOF') and (line != '!'):
                line = lines.pop(0)
                l.append(line)
            line = "\n".join(l)
            dataset[header][line] = OrderedDict()    #add the banner under the header
        elif depth == depth_current:
            dataset[line] = OrderedDict()    #add to the tree
            lines.pop(0)
        elif depth > depth_current:    #depth change trigger setting the header, recursion
            header = next(reversed(dataset))    #get last entry on the current depth
            dataset[header]['header'] = depth_current
            build_tree (dataset[header], depth, lines)    #recusrive build, step funtion
#

def clean_tree(del_tree_matches, dataset): #remove lines from the dataset that are undesired
    for key in del_tree_matches:
        if key in dataset:
            if del_tree_matches[key] == 1:
                if options.debug:
                    print("deleting line: ", key)
                del dataset[key]
            else:
                clean_tree(del_tree_matches[key], dataset[key])
#

def substitute_lines(lines): #update lines with the "correct" format -- hack, but I can't think of a better way.
    ip_access_list = re.compile('^ip access-list ')

    new_lines = []
    while lines:
        l = lines.pop(0)
        if ip_access_list.match(l):  # looks for ip access-list
            new_lines.append(l)
            while l != '!':
                l = lines.pop(0)
                if l.count('/32'):
                    l = re.sub('(\d+\.\d+\.\d+\.\d+)/32', r'host \1', l) #replace {ip}/32 with host {ip}
                new_lines.append(l)
        else:
            new_lines.append(l)
    return new_lines
#

def dump_ds(dataset):   #output the data within a tree
    output = []
    for key in dataset.keys():
        if key == 'header':
            continue
        output.append(key)
        if 'header' in dataset[key]:    #If we have a header, trigger recusrive dump
            l = dump_ds(dataset[key])
            for x in l:
                output.append(x)
    return output
#

def make_set(unique_set, dataset):
    count = 0
    for key in dataset.keys():
        if options.filter:
            if any(ele in key for ele in options.filter):
                if options.debug:
                    print('filtered: ' + key)
                continue
        if key.lstrip().startswith('!') and options.no_exclamations:    #filter any line starting with !
            if options.debug:
                print('filtered: ' + key)
            continue
        count+=1
        if key in unique_set:
            if count > unique_set[key]:    #on collisions we want the larger number
                unique_set[key] = count
            elif count < unique_set[key]:
                count = unique_set[key]    #jump the count forward to help mantain order
        else:
            unique_set[key] = count
#

def diff_ds(dataset1, dataset2):
    unique_set = {}
        #we need an ordered list of all lines to display the data in order.  Not perfect but maintains positions failrly well.  We use the linecount from the original data to determine order.
    make_set(unique_set, dataset1)
    make_set(unique_set, dataset2)
    output = []
    for entry in sorted(unique_set, key=unique_set.get):
            #this sorts the entry (count) and returns the entrys in order.
        if entry == 'header':    #used for tagging, not needed in output
            continue
        if entry in dataset1:
            if entry in dataset2: #match, further checks needed if tagged with header
                if 'header' in dataset1[entry] and 'header' in dataset2[entry]:
                    #recursive check for equality if both have header tag
                    l = diff_ds(dataset1[entry], dataset2[entry])
                    if len(l) > 0:
                        output.append('  : ' + entry)
                        for x in l:
                            output.append(x)
                elif 'header' in dataset1[entry] or 'header' in dataset2[entry]:
                    #recursive check for changes when one not tagged with header
                    l = diff_ds(dataset1[entry], dataset2[entry])
                    if len(l) > 0:
                        output.append('  : ' + entry)
                        for x in l:
                            output.append(x)
            else:    #old entry missing report everything in this tree
                output.append('- : ' + entry)
                l = dump_ds(dataset1[entry])
                for x in l:
                    output.append('- : ' + x)
        else:    #new entry report everything in this tree
            output.append('+ : ' + entry)
            l = dump_ds(dataset2[entry])
            for x in l:
                output.append('+ : ' + x)
    return output
#

def get_config(file):
    import os
    if os.path.isfile(file):    #check if file is present
        config_file = open(file, "r")        #open text file in read mode
        config = config_file.read()       #read whole file to a list
        config_file.close()         #close file
        lines = config.split('\n')
        for i,s in enumerate(lines):    # strip the line brake data from the list
            lines[i] = s.rstrip()
        lines = substitute_lines(lines)  # replace lines that translate in EOS
        return lines
    else:
        exit('File "{}" was not found'.format(file))
#

def get_command_line():
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
      description='''Compares two configuration files. Returns section headers and changed lines.
      Head of line key:
        : indicates a header that exists in both, followed by a change.
      - : indicates that the line in the first file was removed.
      + : indicates that the line was added in the second file.
      ''')
    parser.add_argument('fn1', metavar='first_config_file')
    parser.add_argument('fn2', metavar='second_config_file')
    parser.add_argument('--no_exclamations', action='store_true',
                        help='deletes any line where the first non space character is !')
    parser.add_argument('--filter', action='append',
                        help='filters matching lines of config. Case sensitive. Note: This will remove sections if the header is matched use --debug to confirm matching lines')
    parser.add_argument('--debug', action='store_true',
                        help='shows lines that match a filter')
    args = parser.parse_args()
    if args.filter:
        options.filter.extend(args.filter)
    if args.debug:
        options.debug = True
    if args.no_exclamations:
        options.no_exclamations = True
    return args.fn1, args.fn2
#

class Opts:
    filter = []
    debug = False
    no_exclamations = False
    del_tree_matches = {
        'management api http-commands' : { '   no protocol http' : 1}
        }
#

def main():
    #setup
    dict1 = OrderedDict()
    dict2 = OrderedDict()
    starting_depth = 0

    file1, file2 = get_command_line()
    lines = get_config (file1)
    build_tree(dict1, starting_depth, lines)
    lines = get_config (file2)
    build_tree(dict2, starting_depth, lines)

    clean_tree(options.del_tree_matches, dict1)
    clean_tree(options.del_tree_matches, dict2)

    output = diff_ds(dict1, dict2)
    for x in output:
        print(x)
#

options = Opts()
main()
