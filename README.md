# Corvault scripts

Required python modules:

* requests
* pyyaml

## corvault-info.py

Show the difference between all corvault nodes. This is removing specific information like temperature and serial number so it can be used with the ``--diff`` option. This is using ClusterShell to run the command on all nodes in parallel and compare the output.

``` bash
clush --diff -w corvault[1-2] --worker=exec python corvault-info.py %host
```

Show the detailed information about a corvault node.

``` bash
python corvault-info.py corvault1 --full
local-controller: A
system-name: REDACTED
serial-number: REDACTED
midplane-serial-number: REDACTED
controller-a-serial-number: REDACTED
controller-b-serial-number: REDACTED

Alerts:
2025-04-25 20:42:19
severity: WARNING
acknowledged: No
description: Enclosure 0, Controller A, Network Port
Health: Degraded
Reason The system was unable to connect using the DNS parameters for this controller.

2025-04-22 20:41:22
severity: WARNING
acknowledged: No
description: Disk Group REDACTED
Health: N/A
Reason The spare capacity available to the ADAPT disk group is not sufficient to meet the required configured spare capacity that is needed to provide full fault tolerance. Spare capacity availability can be influenced by operations that require available space in the system, such as reconstructing data from a failed disk.

2025-03-19 17:47:56
severity: CRITICAL
acknowledged: No
description: Enclosure 0, Disk 100
Health: Fault
Reason Excessive media errors.


fde-security-status: Unsecured
controller-a-status: Operational
controller-b-status: Operational
redundancy-mode: Active-Active ULP
Controller versions:
Controller 0:
bundle-version: S120R002-02
hw-rev: 6.0
gem-version: usm-rss_pods106-v5.3_lite-r2023.35.0_rc1_rel_1226

Controller 1:
bundle-version: S120R002-02
hw-rev: 6.0
gem-version: usm-rss_pods106-v5.3_lite-r2023.35.0_rc1_rel_1226


DNS configuration:
controller: A
name-servers: REDACTED
search-domains: REDACTED
controller: B
name-servers: REDACTED
search-domains: REDACTED

NTP configuration:
ntp-contact-time: none
ntp-server-address: ntp
ntp-status: activated

FDE status:
fde-security-status: Unsecured
import-lock-key-id: 00000001
lock-key-id: 00000001

Volumes:
Volume 0:
virtual-disk-name: REDACTED
health: OK
health-reason
owner: A
progress: 0%
write-policy: write-back

Volume 1:
virtual-disk-name: REDACTED
health: OK
health-reason
owner: B
progress: 0%
write-policy: write-back

Ports:
A0 500c0fff64b40000 Up 12Gb OK
A1 500c0fff64b40100 Disconnected Auto OK
A2 500c0fff64b40200 Up 12Gb OK
A3 500c0fff64b40300 Disconnected Auto OK
B0 500c0fff64b40400 Up 12Gb OK
B1 500c0fff64b40500 Disconnected Auto OK
B2 500c0fff64b40600 Up 12Gb OK
B3 500c0fff64b40700 Disconnected Auto OK

disks:
0 OK The component is healthy. ST24000NM005H REDACTED 46875541504 ET05 24.0TB 25 0
[...]
100 Fault Excessive media errors. ST24000NM005H REDACTED 46875541504 ET05 24.0TB 0 0
[...]
105 OK The component is healthy. ST24000NM005H REDACTED 46875541504 ET05 24.0TB 27 0

sensors:
CPU Temperature-Ctlr B OK 49 C
ASIC Temperature-Ctlr B OK 39 C
Capacitor Pack Temperature-Ctlr B OK 29 C
Expander Temperature-Ctlr B OK 66 C
Disk Controller Temperature-Ctlr B OK 43 C
Disk Controller 2 Temperature-Ctlr B OK 36 C
CPU Temperature-Ctlr A OK 51 C
ASIC Temperature-Ctlr A OK 43 C
Capacitor Pack Temperature-Ctlr A OK 32 C
Expander Temperature-Ctlr A OK 66 C
Disk Controller Temperature-Ctlr A OK 39 C
Disk Controller 2 Temperature-Ctlr A OK 39 C
Capacitor Pack Voltage-Ctlr B OK 10.77
Capacitor Cell 1 Voltage-Ctlr B OK 2.70
Capacitor Cell 2 Voltage-Ctlr B OK 2.70
Capacitor Cell 3 Voltage-Ctlr B OK 2.70
Capacitor Cell 4 Voltage-Ctlr B OK 2.69
Capacitor Pack Voltage-Ctlr A OK 10.80
Capacitor Cell 1 Voltage-Ctlr A OK 2.70
Capacitor Cell 2 Voltage-Ctlr A OK 2.70
Capacitor Cell 3 Voltage-Ctlr A OK 2.70
Capacitor Cell 4 Voltage-Ctlr A OK 2.69
Capacitor Charge-Ctlr B OK 100%
Capacitor Charge-Ctlr A OK 100%
Capacitor Capacitance-Ctlr B OK 5.4 Farads
Capacitor Capacitance-Ctlr A OK 5.4 Farads
Capacitor Resistance-Ctlr B OK 103.9 Ohms
Capacitor Resistance-Ctlr A OK 101.6 Ohms
Overall Unit Status OK OK
Midplane 0 Temperature OK 32 C
Midplane 1 Temperature OK 30 C
Temperature Core 2 Hotspot Loc: right-PSU OK 31 C
Temperature Core 2 Inlet Loc: right-PSU OK 40 C
Temperature Core 2 Exhaust Loc: right-PSU OK 38 C
Temperature Core 0 Hotspot Loc: left-PSU OK 30 C
Temperature Core 0 Inlet Loc: left-PSU OK 39 C
Temperature Core 0 Exhaust Loc: left-PSU OK 37 C
10 drive Baseplane Temperature Loc: Baseplane 4 OK 21 C
Baseplane Slot 0 Temperature Loc: Baseplane 3 OK 30 C
Baseplane Slot 1 Temperature Loc: Baseplane 3 OK 30 C
Expander Slot 0 Temperature Loc: Baseplane 3 OK 55 C
Expander Slot 1 Temperature Loc: Baseplane 3 OK 64 C
Baseplane Slot 0 Temperature Loc: Baseplane 2 OK 28 C
Baseplane Slot 1 Temperature Loc: Baseplane 2 OK 28 C
Expander Slot 0 Temperature Loc: Baseplane 2 OK 61 C
Expander Slot 1 Temperature Loc: Baseplane 2 OK 56 C
Baseplane Slot 0 Temperature Loc: Baseplane 1 OK 27 C
Baseplane Slot 1 Temperature Loc: Baseplane 1 OK 26 C
Expander Slot 0 Temperature Loc: Baseplane 1 OK 66 C
Expander Slot 1 Temperature Loc: Baseplane 1 OK 64 C
Baseplane Slot 0 Temperature Loc: Baseplane 0 OK 24 C
Baseplane Slot 1 Temperature Loc: Baseplane 0 OK 24 C
Expander Slot 0 Temperature Loc: Baseplane 0 OK 61 C
Expander Slot 1 Temperature Loc: Baseplane 0 OK 59 C
Voltage Core 2 12V Rail Loc: right-PSU OK 12.38
Voltage Core 2 Input Rail Loc: right-PSU OK 242.96
Voltage Core 0 12V Rail Loc: left-PSU OK 12.38
Voltage Core 0 Input Rail Loc: left-PSU OK 242.73
Current Core 2 12V Rail Loc: right-PSU OK 45.54
Current Core 2 Input Rail Loc: right-PSU OK 2.38
Current Core 0 12V Rail Loc: left-PSU OK 42.50
Current Core 0 Input Rail Loc: left-PSU OK 2.22

fans:
Enclosure 0, Fan Module 0 Fan 0 OK 7650
Enclosure 0, Fan Module 0 Fan 1 OK 7620
Enclosure 0, Fan Module 1 Fan 0 OK 7650
Enclosure 0, Fan Module 1 Fan 1 OK 7680
Enclosure 0, Fan Module 2 Fan 0 OK 7650
Enclosure 0, Fan Module 2 Fan 1 OK 7620
Enclosure 0, Fan Module 3 Fan 0 OK 7620
Enclosure 0, Fan Module 3 Fan 1 OK 7680
Enclosure 0, Fan Module 4 Fan 0 OK 8670
Enclosure 0, Fan Module 5 Fan 0 OK 9210
```
