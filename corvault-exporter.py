from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import corvault


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; version=0.0.4')
        self.end_headers()
        hostname = self.path.split('/')[1]

        c = corvault.Corvault(hostname)
        c.load_config()
        c.login()
        self.wfile.write(b'# HELP corvault_sensor sensor values\n')
        self.wfile.write(b'# TYPE corvault_sensor gauge\n')
        sensors = c.get_page('/api/show/sensor-status')['sensors']
        for sensor in sensors:
            if sensor['sensor-name'] == 'Overall Unit Status':
                value = sensor['status-numeric']
            elif sensor['value'] == '':  # Can happen when a PSU is not powered
                value = -1
            else:
                try:
                    value = float(sensor['value'].split(' ')[0].rstrip('%'))
                except ValueError:
                    print(f"Could not convert {sensor['value']} to float on {sensor['sensor-name']}")
                    value = -1
            name = sensor['sensor-name'].replace(' ', '_').replace('-', '_').replace(':', '')
            self.wfile.write(f'corvault_sensor{{name="{name}"}} {value}\n'.encode())

        self.wfile.write(b'# HELP corvault_fan fan speed\n')
        self.wfile.write(b'# TYPE corvault_fan gauge\n')
        for fan in c.get_page('/api/show/fans')['fan']:
            module = fan['location'][-1]
            fan_number = fan['name'][-1]
            self.wfile.write(f'corvault_fan{{module="{module}",fan="{fan_number}"}} {fan["speed"]}\n'.encode())

        disks = sorted(c.get_page('/api/show/disks')['drives'], key=lambda x: x['slot'])
        self.wfile.write(b'# HELP corvault_disk_health disk health\n')
        self.wfile.write(b'# TYPE corvault_disk_health gauge\n')
        for disk in disks:
            self.wfile.write(f'corvault_disk_health{{slot="{disk["slot"]}",model="{disk["model"]}",\
serial_number="{disk["serial-number"]}",revision="{disk["revision"]}"}} {disk["health-numeric"]}\n'.encode())

        self.wfile.write(b'# HELP corvault_disk_temperature disk temperature\n')
        self.wfile.write(b'# TYPE corvault_disk_temperature gauge\n')
        for disk in disks:
            self.wfile.write(f'corvault_disk_temperature{{slot="{disk["slot"]}",model="{disk["model"]}",\
serial_number="{disk["serial-number"]}",revision="{disk["revision"]}"}} {disk["temperature-numeric"]}\n'.encode())

        self.wfile.write(b'# HELP corvault_disk_transferred_total disk data transferred\n')
        self.wfile.write(b'# TYPE corvault_disk_transferred_total counter\n')
        for disk in disks:
            self.wfile.write(f'corvault_disk_transferred_total{{slot="{disk["slot"]}",model="{disk["model"]}",\
serial_number="{disk["serial-number"]}",revision="{disk["revision"]}"}} {disk["total-data-transferred-numeric"]}\n'.encode())

        # might be useful once disks are remanufactured to remove a platter
        # self.wfile.write(b'# HELP corvault_disk_size Corvault disk size\n')
        # self.wfile.write(b'# TYPE corvault_disk_size gauge\n')
        # for disk in disks:
        #     self.wfile.write(f'corvault_disk_size{{slot="{disk["slot"]}",model="{disk["model"]}",\
        # serial_number="{disk["serial-number"]}",revision="{disk["revision"]}"}} {disk["size-numeric"]}\n'.encode())

        disk_groups = c.get_page('/api/show/disk-groups')['disk-groups']
        self.wfile.write(b'# HELP corvault_disk_group_status \n')
        self.wfile.write(b'# TYPE corvault_disk_group_status gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_status{{name="{group["name"]}"}} {group["status-numeric"]}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_write_back_enabled \n')
        self.wfile.write(b'# TYPE corvault_disk_group_write_back_enabled gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_write_back_enabled{{name="{group["name"]}"}} {group["write-back-enabled-numeric"]}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_current_job \n')
        self.wfile.write(b'# TYPE corvault_disk_group_current_job gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_current_job{{name="{group["name"]}"}} {group["current-job-numeric"]}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_current_job_completion \n')
        self.wfile.write(b'# TYPE corvault_disk_group_current_job_completion gauge\n')
        for group in disk_groups:
            progress = group["current-job-completion"].rstrip('%')
            self.wfile.write(f'corvault_disk_group_current_job_completion{{name="{group["name"]}"}} {progress}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_critical_capacity \n')
        self.wfile.write(b'# TYPE corvault_disk_group_critical_capacity gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_critical_capacity{{name="{group["name"]}"}} {group["critical-capacity-numeric"]}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_degraded_capacity \n')
        self.wfile.write(b'# TYPE corvault_disk_group_degraded_capacity gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_degraded_capacity{{name="{group["name"]}"}} {group["degraded-capacity-numeric"]}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_health \n')
        self.wfile.write(b'# TYPE corvault_disk_group_health gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_health{{name="{group["name"]}"}} {group["health-numeric"]}\n'.encode())
        self.wfile.write(b'# HELP corvault_disk_group_health_reason \n')
        self.wfile.write(b'# TYPE corvault_disk_group_health_reason gauge\n')
        for group in disk_groups:
            self.wfile.write(f'corvault_disk_group_health_reason{{name="{group["name"]}"}} {group["health-reason-numeric"]}\n'.encode())


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    server = ThreadingSimpleServer(('0.0.0.0', 8080), Handler)
    server.serve_forever()


if __name__ == '__main__':
    run()
