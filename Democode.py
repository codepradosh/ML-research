#!/bin/sh
''''which python2 >/dev/null 2>&1 && exec python2 "$0" "$@" # '''
''''which python3 >/dev/null 2>&1 && exec python3 "$0" "$@" # '''
''''which python >/dev/null 2>&1 && exec python "$0" "$@" # '''

#!/usr/bin/env python

import subprocess
import sys

def get_csb_version():
    try:
        result = subprocess.Popen(['csb', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error_output = result.communicate()
        output = output.strip()
        error_output = error_output.strip()
        
        if result.returncode != 0:
            print('Error getting CSB version: {}'.format(error_output))
            sys.exit(1)
        
        # Extract the first digit of the CSB version (e.g., 3.x.x, 4.x.x, 8.x.x)
        csb_version = int(output.split('.')[0])
        return csb_version
    except Exception as e:
        print('Error getting CSB version: {}'.format(e))
        sys.exit(1)

def execute_service_command(service_name, action, csb_version):
    if csb_version == 3:
        # For CSB version 3, use 'dzdo service' commands
        if action == 'start':
            command = 'dzdo service {0} start'.format(service_name)
        elif action == 'stop':
            command = 'dzdo service {0} stop'.format(service_name)
        elif action == 'status':
            command = 'dzdo service {0} status'.format(service_name)
        elif action == 'restart':
            command = 'dzdo service {0} stop && dzdo service {0} start'.format(service_name)
        else:
            print('Invalid action. Use one of: start, stop, restart, status')
            sys.exit(1)
    elif csb_version in (4, 8):
        # For CSB version 4 and 8, use 'dzdo systemctl' commands
        if action == 'start':
            command = 'dzdo systemctl start {0}'.format(service_name)
        elif action == 'stop':
            command = 'dzdo systemctl stop {0}'.format(service_name)
        elif action == 'status':
            command = 'dzdo systemctl status {0}'.format(service_name)
        elif action == 'restart':
            command = 'dzdo systemctl stop {0} && dzdo systemctl start {0}'.format(service_name)
        else:
            print('Invalid action. Use one of: start, stop, restart, status')
            sys.exit(1)
    else:
        print('Unsupported CSB version.')
        sys.exit(1)

    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error_output = result.communicate()
        
        if result.returncode != 0:
            error_output = error_output.strip()
            print('Error executing command: {}'.format(error_output))
            sys.exit(1)
        
        print('Service "{0}" {1}ed successfully.'.format(service_name, action))
    except Exception as e:
        print('Error executing command: {}'.format(e))
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: ./DMZ.py <service_name> <action>')
        sys.exit(1)

    service_name = sys.argv[1]
    action = sys.argv[2].lower()  # Action: start, stop, restart, status
    csb_version = get_csb_version()

    execute_service_command(service_name, action, csb_version)
