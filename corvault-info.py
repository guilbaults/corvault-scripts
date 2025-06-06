import corvault
import argparse

FULL_OUTPUT = True


def full_print(*args, **kwargs):
    if FULL_OUTPUT:
        print(*args, **kwargs)
    else:
        # do not print anything
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Corvault Info')
    parser.add_argument('host', type=str, help='Corvault hostname')
    # type of output can be full or diff
    # diff only print things that should be identical between all corvaults
    parser.add_argument('--full', action='store_true', help='Full output (break diff)')
    parser.add_argument('--show-informational', action='store_true', help='Show informational alerts')
    args = parser.parse_args()

    if args.full:
        FULL_OUTPUT = True
    else:
        FULL_OUTPUT = False

    c = corvault.Corvault(args.host)
    c.load_config()
    c.login()

    system = c.get_page('/api/show/system')['system'][0]
    system_parameters = c.get_page('/api/show/system-parameters')['system-parameters-table'][0]
    full_print('local-controller:', system_parameters['local-controller'])
    full_print('system-name:', system['system-name'])
    full_print('serial-number:', system_parameters['serial-number'])
    full_print('midplane-serial-number:', system['midplane-serial-number'])
    full_print('controller-a-serial-number:', system['redundancy'][0]['controller-a-serial-number'])
    full_print('controller-b-serial-number:', system['redundancy'][0]['controller-b-serial-number'])

    print()
    print('Alerts:')
    for alert in c.get_page('/api/show/alerts')['alerts']:
        if alert['resolved'] == 'Yes':
            # skip resolved alerts
            continue
        if alert['severity'] == 'INFORMATIONAL' and args.show_informational is False:
            continue
        full_print(alert['detected-time'])
        print('severity:', alert['severity'])
        print('acknowledged:', alert['acknowledged'])
        print('description:', alert['description'])
        print('Health:', alert['health'])
        print('Reason', alert['reason'])
        print()

    print()
    print('fde-security-status:', system['fde-security-status'])
    print('controller-a-status:', system['redundancy'][0]['controller-a-status'])
    print('controller-b-status:', system['redundancy'][0]['controller-b-status'])
    print('redundancy-mode:', system['redundancy'][0]['redundancy-mode'])

    print('Controller versions:')
    for idx, controller in enumerate(c.get_page('/api/show/versions')['versions']):
        print(f'Controller {idx}:')
        print('bundle-version:', controller['bundle-version'])
        print('hw-rev:', controller['hw-rev'])
        print('gem-version:', controller['gem-version'])
        print()

    print()
    print('DNS configuration:')
    for controller in c.get_page('/api/show/dns-parameters')['dns-parameters']:
        print('controller:', controller['controller'])
        print('name-servers:', controller['name-servers'])
        print('search-domains:', controller['search-domains'])

    print()
    print('NTP configuration:')
    ntp = c.get_page('/api/show/ntp-status')['ntp-status'][0]
    print('ntp-contact-time:', ntp['ntp-contact-time'])
    print('ntp-server-address:', ntp['ntp-server-address'])
    print('ntp-status:', ntp['ntp-status'])

    print()
    print('FDE status:')
    fde = c.get_page('/api/show/fde-state')['fde-state'][0]
    print('fde-security-status:', fde['fde-security-status'])
    full_print('import-lock-key-id:', fde['import-lock-key-id'])
    full_print('lock-key-id:', fde['lock-key-id'])

    print()
    print('Volumes:')
    for idx, volume in enumerate(sorted(c.get_page('/api/show/volumes')['volumes'],
                                 key=lambda x: x['virtual-disk-name'])):
        print(f'Volume {idx}:')
        full_print('virtual-disk-name:', volume['virtual-disk-name'])
        print('health:', volume['health'])
        if volume['health'] != 'OK':
            print('health-reason:', volume['health-reason'])
        print('owner:', volume['owner'])
        full_print('progress:', volume['progress'])
        print('write-policy:', volume['write-policy'])
        print()

    print('Disk groups:')
    for group in c.get_page('/api/show/disk-groups')['disk-groups']:
        if FULL_OUTPUT:
            print(group['name'])
            print('status:', group['status'])
            print('write-back-enabled:', group['write-back-enabled'])
            print('current-job:', group['current-job'])
            print('current-job-completion:', group['current-job-completion'])
            print('critical-capacity:', group['critical-capacity'])
            print('degraded-capacity:', group['degraded-capacity'])
            print('health:', group['health'])
            if group['health'] != 'OK':
                print('health-reason:', group['health-reason'])
            print()
        else:
            if group['health'] != 'OK':
                print(group['status'], group['write-back-enabled'],
                      group['health'], group['health-reason'])
            else:
                print(group['status'], group['write-back-enabled'],
                      group['health'])

    print()
    print('Ports:')
    for port in c.get_page('/api/show/ports')['port']:
        if FULL_OUTPUT:
            print(port['port'], port['target-id'], port['status'], port['actual-speed'], port['health'], port['health-reason'])
        else:
            print(port['port'], port['status'], port['actual-speed'], port['health'], port['health-reason'])

    print()
    print('Disks:')
    for disk in sorted(c.get_page('/api/show/disks')['drives'], key=lambda x: x['slot']):
        if FULL_OUTPUT:
            print(disk['slot'], disk['health'], disk['health-reason'],
                  disk['model'], disk['serial-number'], disk['size-numeric'],
                  disk['revision'], disk['size'], disk['temperature-numeric'], disk['total-data-transferred-numeric'])
        else:
            print(disk['slot'], disk['health'], disk['health-reason'],
                  disk['model'], disk['size-numeric'], disk['revision'], disk['size'])

    print()
    print('Sensors:')
    sensors = c.get_page('/api/show/sensor-status')['sensors']
    for sensor in sensors:
        if FULL_OUTPUT:
            print(sensor['sensor-name'], sensor['status'], sensor['value'])
        else:
            print(sensor['sensor-name'], sensor['status'])

    print()
    print('Fans:')
    for fan in c.get_page('/api/show/fans')['fan']:
        if FULL_OUTPUT:
            print(fan['location'], fan['name'], fan['health'], fan['speed'])
        else:
            print(fan['location'], fan['name'], fan['health'])
