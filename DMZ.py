#!/bin/sh
# This is a Python script, so the shebang should point to the correct Python interpreter
# For Python 2
# #!/usr/bin/env python2

# For Python 3
# #!/usr/bin/env python3

import subprocess
import sys

# rest of your Python script...




import subprocess
import sys

def check_service_status(service_name):
    command = get_validation_command(service_name)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

import subprocess

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
        print('Usage: python script.py <service_name> <build_number>')
        sys.exit(1)

    service_name = sys.argv[1]
    build_number = sys.argv[2]

    status = check_service_status(service_name)
    if status == '1':
        print(f'{service_name} is running.')
    elif status == '0':
        print(f'{service_name} is not running. Restarting the service...')
        stop_service(service_name, build_number)
        start_service(service_name, build_number)
        print(f'{service_name} restarted successfully.')
    else:
        print(f'Failed to get the status of {service_name}.')
        

        
        
        
        
        
        
        
        
        
        
        
        
        
import subprocess
import sys


def check_service_status(service_name, build_number):
    command = get_validation_command(service_name, build_number)
    try:
        if sys.version_info < (3, 0):
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
        else:
            result = subprocess.run(command, shell=True, capture_output=True)
            stdout = result.stdout
            stderr = result.stderr

        return stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print("Error occurred while checking service status: {0}".format(e))
        sys.exit(1)


def get_validation_command(service_name, build_number):
    commands = {
        'dcagentd': {
            'CSL3': 'sudo /sbin/service dcagentd status | grep running | wc -l',
            'CSL4': 'sudo systemctl status dcagentd.service | grep "Active: active (running)" | wc -l',
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent status | grep running | wc -l',
            'CSL4': 'sudo systemctl status splunkagent.service | grep "Active: active (running)" | wc -l',
        },
        # Add other service and command mappings here
    }
    return commands.get(service_name, {}).get(build_number, '')


def stop_service(service_name, build_number):
    stop_command = get_stop_command(service_name, build_number)
    try:
        subprocess.call(stop_command, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred while stopping the service: {0}".format(e))
        sys.exit(1)


def start_service(service_name, build_number):
    start_command = get_start_command(service_name, build_number)
    try:
        subprocess.call(start_command, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred while starting the service: {0}".format(e))
        sys.exit(1)


def get_stop_command(service_name, build_number):
    stop_commands = {
        'dcagentd': {
            'CSL3': 'sudo /sbin/service dcagentd stop',
            'CSL4': 'sudo systemctl stop dcagentd.service',
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent stop',
            'CSL4': 'sudo systemctl stop splunkagent.service',
        },
        # Add other service and command mappings here
    }
    return stop_commands.get(service_name, {}).get(build_number, '')


def get_start_command(service_name, build_number):
    start_commands = {
        'dcagentd': {
            'CSL3': 'sudo /sbin/service dcagentd start',
            'CSL4': 'sudo systemctl start dcagentd.service',
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent start',
            'CSL4': 'sudo systemctl start splunkagent.service',
        },
        # Add other service and command mappings here
    }
    return start_commands.get(service_name, {}).get(build_number, '')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python script.py [service_name] [build_number]')
        sys.exit(1)

    service_name = sys.argv[1]
    build_number = sys.argv[2]

    status = check_service_status(service_name, build_number)
    if status == '1':
        print('{0} is running.'.format(service_name))
    elif status == '0':
        print('{0} is not running. Restarting the service...'.format(service_name))
        stop_service(service_name, build_number)
        start_service(service_name, build_number)
        print('{0} restarted successfully.'.format(service_name))
    else:
        print('Failed to get the status of {0}.'.format(service_name))
















result_df['Time'] = pd.to_datetime(result_df['Time'])  # Convert 'Time' column to datetime

# Filter the data points above the threshold
above_threshold_df = result_df[result_df['Composite Score'] > threshold]

# Merge with the original dataset to get the corresponding data
merged_df = pd.merge(above_threshold_df, df, on='Time', how='inner')

# Print the resulting dataframe
print(merged_df)

# Plot the composite scores within the zoomed time range
plt.figure(figsize=(10, 6))
plt.plot(zoomed_df['Time'], zoomed_df['Composite Score'], color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.scatter(above_threshold_df['Time'], above_threshold_df['Composite Score'], color='red', label='Above Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Zoomed Composite Function Graph')
plt.legend()
plt.xlim(start_time, end_time)  # Set the x-axis limits
plt.show()

        
        
        
        
# Step 10: Set the threshold
threshold = np.percentile(composite_scores, 95)

# Step 11: Identify time frames above the threshold
above_threshold_df = combined_df[combined_df['Composite Score'] > threshold]

# Step 12: Print the time frames and relevant columns above the threshold
print("Time frames and relevant columns above the threshold:")
print(above_threshold_df[['Time', 'Composite Score', 'Average_IO', 'Queue_Size', 'IO_Time']])

        

# Export composite scores to CSV
composite_scores_df = pd.DataFrame({'Time': combined_df['Time'], 'Composite Score': composite_scores})
composite_scores_df.to_csv('composite_scores.csv', index=False)

        
        
        
        
        
        
        
