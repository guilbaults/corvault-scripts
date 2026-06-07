#!/usr/bin/env python
import corvault
import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='icinga checks for Corvault')
    parser.add_argument('--host', type=str, help='Corvault hostname', required=True)
    args = parser.parse_args()

    c = corvault.Corvault(args.host)
    c.load_config()
    c.login()
    criticals = []
    warnings = []

    for alert in c.get_page('/api/show/alerts')['alerts']:
        alert_text = f'[{alert["severity"]}] {alert["description"]} - {alert["reason"]}'
        if alert['resolved'] == 'Yes':
            # skip resolved alerts
            continue
        if alert['severity'] == 'INFORMATIONAL':
            continue
        if alert['health-numeric'] == 4:
            # skip health-numeric 4 alerts
            # The spare capacity available to the ADAPT disk group is not sufficient to meet the required configured spare capacity that is needed to provide full fault tolerance
            continue
        if alert['severity'] == 'CRITICAL':
            criticals.append(alert_text)
        elif alert['severity'] == 'WARNING':
            warnings.append(alert_text)
        print(alert_text)

    disks = sorted(c.get_page('/api/show/disks')['drives'], key=lambda x: x['slot'])
    largest_disk_size = max(int(disk['size-numeric']) for disk in disks)
    found_slots = set()
    for disk in disks:
        # check for failed disks or empty slots
        if disk['health'] != 'OK':
            if disk['health-reason'] == 'The disk is degraded due to a pending or active preemptive reconstruct operation.':
                print(f'[WARNING] - Disk in slot {disk["slot"]} has health status {disk["health"]} because of preemptive reconstruct operation')
                warnings.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} because of preemptive reconstruct operation')
            elif disk['health-reason'] == 'The disk may contain invalid metadata.':
                print(f'[CRITICAL] - Disk in slot {disk["slot"]} contain invalid metadata.')
                criticals.append(f'Disk in slot {disk["slot"]} contain invalid metadata.')
            elif disk['health-reason'] == 'A disk that was previously a member of a disk group has been detected.':
                print(f'[CRITICAL] - Disk in slot {disk["slot"]} was previously a member of a disk group has been detected.')
                criticals.append(f'Disk in slot {disk["slot"]} was previously a member of a disk group has been detected.')
            elif disk['health-reason'] == 'The system determined that the indicated disk is degraded because it experienced a number of disk errors in excess of a configured threshold.':
                print(f'[WARNING] - Disk in slot {disk["slot"]} has health status {disk["health"]} because it experienced a number of disk errors in excess of a configured threshold.')
                warnings.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} because it experienced a number of disk errors in excess of a configured threshold.')
            elif disk['health-reason'] == 'A user forced the disk out of the disk group.':
                print(f'[WARNING] - Disk in slot {disk["slot"]} has health status {disk["health"]} {disk["health-reason"]}')
                warnings.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} {disk["health-reason"]}')
            else:
                print(f'[CRITICAL] - Disk in slot {disk["slot"]} has health status {disk["health"]} {disk["health-reason"]}')
                criticals.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} {disk["health-reason"]}')

        if int(disk['size-numeric']) < largest_disk_size:
            print(f'[INFO] - Disk in slot {disk["slot"]} has smaller size than the largest disk')

        found_slots.add(disk['slot'])

    for i in range(106):
        if i not in found_slots:
            print(f'[CRITICAL] - Expected disk in slot {i} is missing')
            criticals.append(f'Expected disk in slot {i} is missing')

    if len(criticals) > 0:
        sys.exit(2)
    elif len(warnings) > 0:
        sys.exit(1)
    else:
        print("[OK] - No alerts")
        sys.exit(0)
