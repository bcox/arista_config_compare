# arista_config_compare

```
usage: config_compare.py [-h] [--filter FILTER] [--debug]
                         first_config_file second_config_file

Compares two configuration files. Returns section headers and changed lines.
      Head of line key:
        : indicates a header that exists in both, followed by a change.
      - : indicates that the line in the first file was removed.
      + : indicates that the line was added in the second file.


optional arguments:
  -h, --help          show this help message and exit
  --filter FILTER     filters matching lines of config. Case sensitive. Note:
                      This will remove sections if the header is matched use
                      --debug to confirm matching lines
  --debug             shows lines that match a filter
```

### returns changes in the following format
```
  : interface Port-Channel20
- :    no switchport
  : interface Port-Channel110
- :    mtu 7777
+ :    mtu 4444
  : interface Ethernet1/1
- :    load-interval 120
+ :    load-interval 30
- :    channel-group 110 mode on
+ :    channel-group 110 mode active
  : interface Loopback0
+ :    ip address 10.0.0.1/32
- :    ip address 10.0.0.2/32
- :    isis metric 11
+ :    isis metric 66
  : interface Management1
- :    ip address 10.254.254.240/23
+ :    ip address 10.254.254.240/24
  : ipv6 access-list IPv6-TEST-FILTER
+ :    10 permit tcp fe80::/35 any
- :    10 permit udp fe80::/35 any
  : ip access-list IPv4-TEST-FILTER
+ :    20 permit ip 10.0.0.0/8 any
- :    20 permit ip 10.0.0.0/16 any
  : ip prefix-list IPv4-LONG-PFX
+ :    seq 230 permit 10.22.0.0/16 le 32
- :    seq 230 permit 10.221.0.0/16 le 32
+ : router bgp 36550
+ :    distance bgp 20 200 200
+ :    maximum-paths 6
  : banner login
- : WARNING: This system is solely for the use of authorized employees.
EOF
+ : WARNING: This system is solely for the use of authorized employees and
contractors.
EOF
```
