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
    exit_code = 0

    for alert in c.get_page('/api/show/alerts')['alerts']:
        if alert['resolved'] == 'Yes':
            # skip resolved alerts
            continue
        if alert['severity'] == 'INFORMATIONAL':
            continue
        print(f'[{alert["severity"]}] {alert["description"]} - {alert["reason"]}')
        if alert['severity'] == 'CRITICAL':
            exit_code = 2
        else:
            if exit_code == 0:
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
