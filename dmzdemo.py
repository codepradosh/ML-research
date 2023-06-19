import subprocess
import sys

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


# Rest of the code...



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
            'CSL4': 'sudo systemctl status dcagentd.service | grep "Active: active (running)" | wc -l'
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent status | grep running | wc -l',
            'CSL4': 'sudo systemctl status splunkagent.service | grep "Active: active (running)" | wc -l'
        }
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
            'CSL4': 'sudo systemctl stop dcagentd.service'
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent stop',
            'CSL4': 'sudo systemctl stop splunkagent.service'
        }
        # Add other service and command mappings here
    }
    return stop_commands.get(service_name, {}).get(build_number, '')


def get_start_command(service_name, build_number):
    start_commands = {
        'dcagentd': {
            'CSL3': 'sudo /sbin/service dcagentd start',
            'CSL4': 'sudo systemctl start dcagentd.service'
        },
        'splunkd': {
            'CSL3': 'sudo /sbin/service splunkagent start',
            'CSL4': 'sudo systemctl start splunkagent.service'
        }
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
