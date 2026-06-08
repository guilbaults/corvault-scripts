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
    infos = []

    for alert in c.get_page('/api/show/alerts')['alerts']:
        alert_text = f'{alert["description"]} - {alert["reason"]}'
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

    disks = sorted(c.get_page('/api/show/disks')['drives'], key=lambda x: x['slot'])
    largest_disk_size = max(int(disk['size-numeric']) for disk in disks)
    found_slots = set()
    for disk in disks:
        # check for failed disks or empty slots
        if disk['health'] != 'OK':
            if disk['health-reason'] == 'The disk is degraded due to a pending or active preemptive reconstruct operation.':
                warnings.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} because of preemptive reconstruct operation')
            elif disk['health-reason'] == 'The disk may contain invalid metadata.':
                criticals.append(f'Disk in slot {disk["slot"]} contain invalid metadata.')
            elif disk['health-reason'] == 'A disk that was previously a member of a disk group has been detected.':
                criticals.append(f'Disk in slot {disk["slot"]} was previously a member of a disk group has been detected.')
            elif disk['health-reason'] == 'The system determined that the indicated disk is degraded because it experienced a number of disk errors in excess of a configured threshold.':
                warnings.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} because it experienced a number of disk errors in excess of a configured threshold.')
            elif disk['health-reason'] == 'A user forced the disk out of the disk group.':
                warnings.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} {disk["health-reason"]}')
            else:
                criticals.append(f'Disk in slot {disk["slot"]} has health status {disk["health"]} {disk["health-reason"]}')

        if int(disk['size-numeric']) < largest_disk_size:
            infos.append(f'Disk in slot {disk["slot"]} has smaller size than the largest disk')

        found_slots.add(disk['slot'])

    for i in range(106):
        if i not in found_slots:
            criticals.append(f'Expected disk in slot {i} is missing')

    for group in c.get_page('/api/show/disk-groups')['disk-groups']:
        if group['job-running'] == 'RCON':
            criticals.append(f'Disk group {group["name"]} is rebuilding')
        elif group['job-running'] == 'RBAL':
            infos.append(f'Disk group {group["name"]} is rebalancing')
        elif group['job-running'] == 'VRSC':
            infos.append(f'Disk group {group["name"]} is scrubbing')
        elif group['job-running'] == 'PRERCON':
            warnings.append(f'Disk group {group["name"]} is performing preemptive reconstruct')
        else:
            criticals.append(f'Disk group {group["name"]} is performing unknown job {group["job-running"]}')
        if (group['actual-spare-capacity-numeric'] / group['target-spare-capacity-numeric']) < 0.5:
            criticals.append(f'Disk group {group["name"]} has less than 50% of the target spare capacity available')

    for crit in criticals:
        print(f'[CRITICAL] - {crit}')
    for warn in warnings:
        print(f'[WARNING] - {warn}')
    for info in infos:
        print(f'[INFO] - {info}')

    if len(criticals) > 0:
        sys.exit(2)
    elif len(warnings) > 0:
        sys.exit(1)
    else:
        print("[OK] - No alerts")
        sys.exit(0)
