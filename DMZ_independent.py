python script.py start/stop/restart/status <service_name>
./DMZ_2.py status splunkd



#!/bin/sh
''''which python2 >/dev/null 2>&1 && exec python2 "$0" "$@" # '''
''''which python3 >/dev/null 2>&1 && exec python3 "$0" "$@" # '''
''''which python >/dev/null 2>&1 && exec python "$0" "$@" # '''

import subprocess
import sys
import logging


def get_build_number():
    try:
        result = subprocess.run(['csb', 'version'], stdout=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        # Extract the build number from the output, assuming it's in the format "Build: <build_number>"
        build_number = output.split(': ')[1]
        return build_number
    except Exception as e:
        print(f'Error getting build number: {e}')
        sys.exit(1)

def check_service_status(service_name):
    command = get_validation_command(service_name)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_validation_command(service_name):
    commands = {
        'dcagentd': 'sudo /sbin/service dcagentd status | grep running | wc -',
        'splunkd': 'sudo /sbin/service splunkagent status | grep running | wc -',
        'nscd': 'sudo /etc/init.d/nscd status | grep running | wc -',
        'rpcbind': 'sudo /sbin/service rpcbind status | grep running | wc -',
        'syslogd': 'sudo /etc/init.d/syslog status | grep syslog | grep running | wc -',
        'rsyslogd': 'sudo /etc/init.d/rsyslog status | grep syslog | grep running | wc -',
        'syslog-ng': 'sudo /sbin/service syslog-ng status | grep running | wc -',
        'sendmail-root': 'ps -ef | grep sendmail | grep -v grep | grep root | wc -',
        'sendmail-smmsp': 'ps -ef | grep ntplog | grep -v grep | grep smmsp | wc -',
        'ntplogger': 'ps -ef | grep ntplog | grep -v grep | wc -',
        'ntpd': 'sudo /etc/init.d/ntpd status | grep running | wc -',
        'portmap': 'sudo /etc/init.d/portmap status | grep running | wc -',
        'rscd': 'ps -ef | grep bin/rscd | grep -v grep | wc -',
        'klogd': 'sudo /etc/init.d/syslog status | grep klog | grep running | wc -',
        'crond': 'sudo /etc/init.d/crond status | grep running | wc -',
        'xinetd': 'sudo /sbin/service xinetd status | grep running | wc -',
        'cloak-java': '',
        'TimeKeeperApp': 'sudo /etc/init.d/timekeeper status | grep "Timekeeper is running" | wc -',
        'TKAudit sudo': '/sbin/service tkaudit status | grep "is running" | wc -',
        'crond': '',
        'rsyslog': '',
        'splunkd-root': 'sudo /sbin/service splunkagent status | grep running | wc -',
        'rpcbind-rpc': 'sudo /sbin/service rpcbind status | grep running | wc -',
        'bgl_monitord': 'ps -ef | grep -i bgl | grep -v grep | wc -',
        'crld': 'ps -ef | grep -i crld | grep -v grep | wc -',
        'auditd': 'ps -ef | grep -i auditd | grep -v grep | grep -v kaud | wc -',
        'FALCOND_MEMORY': 'ps -ef | grep goferd_memory sudo /sbin/service goferd status | grep -v grep | grep -i "is running" | wc -',
        'goferd_memory': 'sudo /sbin/service goferd status | grep -v grep | grep -i "is running" | wc -',
        'adclient': 'ps -ef | grep -i adclient | grep -v grep | wc -',
        'pkicrld': 'ps -ef | grep -i crld | grep -v grep | wc -',
        'chronylogger': 'sudo systemctl status chronylogger | grep -v grep | grep -i "active(running)" | wc -',
        'FALCOND': 'ps -ef | grep -i falcon-sensor | grep -v grep | wc -',
        'FALCONSENSOR': 'ps -ef | grep -i falcon-sensor | grep -v grep | wc -',
    }
    return commands.get(service_name, '')


def start_service(service_name, build_number):
    command = get_start_command(service_name, build_number)
    if command:
        subprocess.run(command, shell=True)

def get_start_command(service_name, build_number):
    commands = {
        'dcagentd': {
            'CSL3': 'sudo /sbin/service dcagentd start',
            'CSL4': 'sudo systemctl start; echo $?'
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent start',
            'CSL4': 'sudo /etc/init.d/splunkagent start'
        },
        'nscd': {
            'CSL3': 'sudo /etc/init.d/nscd start',
            'CSL4': 'sudo systemctl start nscd; echo $?'
        },
        'rpcbind': {
            'CSL3': 'sudo /sbin/service rpcbind start',
            'CSL4': 'sudo systemctl start rpcbind; echo $?'
        },
        'syslogd': {
            'CSL3': 'sudo /etc/init.d/syslog start',
            'CSL4': ''
        },
        'rsyslogd': {
            'CSL3': 'sudo /etc/init.d/rsyslog start',
            'CSL4': 'sudo systemctl start rsyslog.service; echo $?'
        },
        'syslog-ng': {
            'CSL3': 'sudo /sbin/service syslog-ng start',
            'CSL4': ''
        },
        'sendmail-root': {
            'CSL3': 'sudo /etc/init.d/sendmail start',
            'CSL4': 'sudo systemctl start sendmail; echo $?'
        },
        'sendmail-smmsp': {
            'CSL3': 'sudo /etc/init.d/sendmail start',
            'CSL4': 'sudo systemctl start sendmail; echo $?'
        },
        'ntplogger': {
            'CSL3': 'sudo /etc/init.d/ntpd start',
            'CSL4': 'sudo systemctl start ntplogger; echo $?'
        },
        'ntpd': {
            'CSL3': 'sudo /etc/init.d/ntpd start',
            'CSL4': 'sudo systemctl start ntpd; echo $?'
        },
        'portmap': {
            'CSL3': '/etc/init.d/portmap start',
            'CSL4': ''
        },
        'rscd': {
            'CSL3': 'sudo /etc/init.d/rscd start',
            'CSL4': ''
        },
        'klogd': {
            'CSL3': 'sudo /etc/init.d/syslog start',
            'CSL4': ''
        },
        'cron': {
            'CSL3': 'sudo /etc/init.d/crond start',
            'CSL4': 'sudo systemctl start crond; echo $?'
        },
        'xinetd': {
            'CSL3': 'sudo /sbin/service xinetd start',
            'CSL4': 'sudo systemctl start xinetd; echo $?'
        },
        'cloak-java': {
            'CSL3': '',
            'CSL4': ''
        },
        'TimeKeeperApp': {
            'CSL3': 'sudo /etc/init.d/timekeeper start',
            'CSL4': 'sudo /etc/init.d/timekeeper start'
        },
        'TKAudit': {
            'CSL3': 'sudo /sbin/service tkaudit start',
            'CSL4': 'sudo /etc/init.d/tkaudit start'
        },
        'crond': {
            'CSL3': '',
            'CSL4': 'sudo systemctl start crond; echo $?'
        },
        'rsyslog': {
            'CSL3': '',
            'CSL4': 'sudo systemctl start rsyslog.service; echo $?'
        },
        'splunkd-root': {
            'CSL3': 'sudo /sbin/service splunkagent start',
            'CSL4': 'sudo /etc/init.d/splunkagent start'
        },
        'rpcbind-rpc': {
            'CSL3': 'sudo /sbin/service rpcbind start',
            'CSL4': 'sudo systemctl start rpcbind; echo $?'
        },
        'bgl_monitord': {
            'CSL3': 'sudo /etc/init.d/bgl_monitor start',
            'CSL4': 'sudo systemctl start bgl_monitor'
        },
        'crld': {
            'CSL3': 'sudo /etc/init.d/crld start',
            'CSL4': 'sudo systemctl start crld'
        },
        'auditd': {
            'CSL3': 'sudo /usr/sbin/service auditd start',
            'CSL4': 'sudo systemctl start auditd.service'
        },
        'FALCOND_MEMORY': {
            'CSL3': 'sudo service falcon-sensor restart',
            'CSL4': 'sudo systemctl restart falcon-sensor.service; echo $?'
        },
        'goferd_memory': {
            'CSL3': 'sudo /sbin/service goferd start',
            'CSL4': 'sudo /bin/systemctl restart goferd'
        },
        'adclient': {
            'CSL3': '',
            'CSL4': ''
        },
        'pkicrld': {
            'CSL3': 'sudo /etc/init.d/crld start',
            'CSL4': 'sudo systemctl status crld | grep Active | grep -i running | wc -'
        },
        'chronylogger': {
            'CSL3': '',
            'CSL4': 'sudo systemctl status chronylogger | grep -v grep | grep -i "active(running)" | wc -'
        },
        'FALCOND': {
            'CSL3': 'sudo service falcon-sensor restart',
            'CSL4': 'sudo systemctl status falcon-sensor.service | grep "Active: active (running)" | wc -'
        },
        'FALCONSENSOR': {
            'CSL3': 'sudo service falcon-sensor restart',
            'CSL4': 'sudo systemctl status falcon-sensor.service | grep "Active: active (running)" | wc -'
        }
    }

    
    return commands.get(service_name, {}).get(build_number, '')

def stop_service(service_name, build_number):
    command = get_stop_command(service_name, build_number)
    if command:
        subprocess.run(command, shell=True)

def get_stop_command(service_name, build_number):
    commands = {
        'dcagentd': {
            'CSL3': 'sudo /sbin/service dcagentd stop',
            'CSL4': 'sudo /etc/init.d/dcagent stop'
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent stop',
            'CSL4': 'sudo /etc/init.d/splunkagent stop'
        },
        'nscd': {
            'CSL3': 'sudo systemctl stop nscd',
            'CSL4': 'sudo systemctl stop nscd'
        },
        'rpcbind': {
            'CSL3': 'sudo systemctl start rpcbind',
            'CSL4': 'sudo systemctl start rpcbind'
        },
        'syslogd': {
            'CSL3': '',
            'CSL4': ''
        },
        'rsyslogd': {
            'CSL3': 'sudo systemctl stop rsyslog.service',
            'CSL4': 'sudo systemctl stop rsyslog.service'
        },
        'syslog-ng': {
            'CSL3': '',
            'CSL4': ''
        },
        'sendmail-root': {
            'CSL3': 'sudo systemctl stop sendmail',
            'CSL4': 'sudo systemctl stop sendmail'
        },
        'sendmail-smmsp': {
            'CSL3': 'sudo systemctl stop sendmail',
            'CSL4': 'sudo systemctl stop sendmail'
        },
        'ntplogger': {
            'CSL3': 'sudo systemctl stop ntplogger',
            'CSL4': 'sudo systemctl stop ntplogger'
        },
        'ntpd': {
            'CSL3': 'sudo systemctl stop ntpd',
            'CSL4': 'sudo systemctl stop ntpd'
        },
        'portmap': {
            'CSL3': '',
            'CSL4': ''
        },
        'rscd': {
            'CSL3': '',
            'CSL4': ''
        },
        'klogd': {
            'CSL3': '',
            'CSL4': ''
        },
        'cron': {
            'CSL3': 'sudo systemctl stop crond',
            'CSL4': 'sudo systemctl stop crond'
        },
        'xinetd': {
            'CSL3': 'sudo systemctl stop xinetd',
            'CSL4': 'sudo systemctl stop xinetd'
        },
        'cloak-java': {
            'CSL3': '',
            'CSL4': 'sudo /app/cloakware/client/cspmclient/bin/cspmclientd stop'
        },
        'TimeKeeperApp': {
            'CSL3': 'sudo /etc/init.d/timekeeper stop',
            'CSL4': ''
        },
        'TKAudit': {
            'CSL3': 'sudo /etc/init.d/tkaudit stop',
            'CSL4': ''
        },
        'crond': {
            'CSL3': 'sudo systemctl stop crond',
            'CSL4': 'sudo systemctl stop crond'
        },
        'rsyslog': {
            'CSL3': 'sudo systemctl stop rsyslog.service',
            'CSL4': 'sudo systemctl stop rsyslog.service'
        },
        'splunkd-root': {
            'CSL3': 'sudo /etc/init.d/splunkagent stop',
            'CSL4': 'sudo /etc/init.d/splunkagent stop'
        },
        'rpcbind-rpc': {
            'CSL3': 'sudo systemctl start rpcbind',
            'CSL4': 'sudo systemctl start rpcbind'
        },
        'bgl_monitord': {
            'CSL3': 'sudo systemctl stop bgl_monitor',
            'CSL4': 'sudo systemctl stop bgl_monitor'
        },
        'crld': {
            'CSL3': 'sudo systemctl stop crld',
            'CSL4': 'sudo systemctl stop crld'
        },
        'auditd': {
            'CSL3': 'sudo /usr/sbin/service auditd stop',
            'CSL4': 'sudo /usr/sbin/service auditd stop'
        },
        'FALCOND_MEMORY': {
            'CSL3': 'sudo systemctl stop falcon-sensor.service',
            'CSL4': 'sudo systemctl stop falcon-sensor.service'
        },
        'goferd_memory': {
            'CSL3': 'sudo /sbin/service goferd stop',
            'CSL4': 'sudo /bin/systemctl stop goferd'
        },
        'adclient': {
            'CSL3': '',
            'CSL4': ''
        },
        'pkicrld': {
            'CSL3': 'sudo systemctl stop crld',
            'CSL4': 'sudo systemctl stop crld'
        },
        'chronylogger': {
            'CSL3': '',
            'CSL4': 'sudo systemctl stop chronylogger'
        },
        'FALCOND': {
            'CSL3': 'sudo systemctl stop falcon-sensor.service',
            'CSL4': 'sudo systemctl stop falcon-sensor.service'
        },
        'FALCONSENSOR': {
            'CSL3': 'sudo systemctl stop falcon-sensor.service',
            'CSL4': 'sudo systemctl stop falcon-sensor.service'
        }
    }
    

    return commands.get(service_name, {}).get(build_number, '')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python script.py <action> <service_name>')
        sys.exit(1)

    action = sys.argv[1].lower()  # Action: start, stop, restart, status
    service_name = sys.argv[2]
    build_number = get_build_number()

    if action == 'status':
        status = check_service_status(service_name)
        if status == '1':
            print(f'{service_name} is running.')
        elif status == '0':
            print(f'{service_name} is not running.')
        else:
            print(f'Failed to get the status of {service_name}.')
    elif action in ('start', 'stop', 'restart'):
        if action == 'start':
            start_service(service_name, build_number)
        elif action == 'stop':
            stop_service(service_name, build_number)
        elif action == 'restart':
            stop_service(service_name, build_number)
            start_service(service_name, build_number)
        print(f'{service_name} {action}ed successfully.')
    else:
        print('Invalid action. Use one of: start, stop, restart, status')
        sys.exit(1)
