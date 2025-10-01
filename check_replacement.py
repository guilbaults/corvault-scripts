#!/usr/bin/env python
import corvault
import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='icinga checks for Corvault for disk replacement')
    parser.add_argument('--host', type=str, help='Corvault hostname', required=True)
    args = parser.parse_args()

    c = corvault.Corvault(args.host)
    c.load_config()
    c.login()
    exit_code = 0

    # The system is not ready for a disk replacement if any disk group is rebuilding or rebalancing
    for group in c.get_page('/api/show/disk-groups')['disk-groups']:
        if group['job-running'] == 'RCON' or group['job-running'] == 'RBAL':
            print(f'[OK] Disk group {group["name"]} is rebuilding or rebalancing. Not ready for a replacement yet.')
            sys.exit(0)

    # Check the health of each disk
    for disk in sorted(c.get_page('/api/show/disks')['drives'], key=lambda x: x['slot']):
        if disk['health'] != 'OK':
            print(f'[WARNING] Disk {disk["serial-number"]} in slot {disk["slot"]} has health status {disk["health"]} - {disk["health-reason"]}')
            exit_code = 1

    if exit_code == 0:
        print("[OK] - No alerts")
        sys.exit(0)
    elif exit_code == 1:
        sys.exit(1)
    elif exit_code == 2:
        sys.exit(2)
    else:
        print("[UNKNOWN] - Unknown error")
        sys.exit(3)
