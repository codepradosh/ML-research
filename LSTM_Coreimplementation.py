#!/bin/sh
''''which python2 >/dev/null 2>&1 && exec python2 "$0" "$@" # '''
''''which python3 >/dev/null 2>&1 && exec python3 "$0" "$@" # '''
''''which python >/dev/null 2>&1 && exec python "$0" "$@" # '''



#!/usr/bin/env python



import subprocess
import sys
import locale

# Determine the system's default encoding
default_encoding = locale.getpreferredencoding()

def get_csb_version():
    try:
        result = subprocess.Popen(['csb', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error_output = result.communicate()
        output = output.strip().decode(default_encoding)
        error_output = error_output.strip().decode(default_encoding)

        if result.returncode != 0:
            print('Error getting CSB version: {}'.format(error_output))
            sys.exit(1)

        # Extract the first digit of the CSB version (e.g., 3.x.x, 4.x.x, 8.x.x)
        csb_version = int(output.split('.')[0])
        return csb_version
    except Exception as e:
        print('Error getting CSB version: {}'.format(e))
        sys.exit(1)

def check_service_status(service_name, csb_version):
    try:
        if csb_version in (4, 8):
            result = subprocess.Popen(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = result.communicate()
            return output.strip().decode(default_encoding)  # Decode using the default encoding
        elif csb_version == 3:
            result = subprocess.Popen(['service', service_name, 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = result.communicate()
            
            if "running" in output.decode(default_encoding).lower():
                return "active"
            else:
                return "inactive"
        else:
            print('Unsupported CSB version.')
            sys.exit(1)
    except Exception as e:
        print('Error checking service status: {}'.format(e))
        sys.exit(1)

def restart_service_if_inactive(service_name, csb_version):
    status = check_service_status(service_name, csb_version)
    if status == 'inactive' or status == 'stopped':
        try:
            if csb_version == 3:
                # For CSB version 3, use 'dzdo service' commands
                subprocess.Popen(['dzdo', 'service', service_name, 'stop'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
                subprocess.Popen(['dzdo', 'service', service_name, 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
            elif csb_version in (4, 8):
                # For CSB versions 4 and 8, use 'dzdo systemctl' commands
                subprocess.Popen(['dzdo', 'systemctl', 'stop', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
                subprocess.Popen(['dzdo', 'systemctl', 'start', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
            else:
                print('Unsupported CSB version.')
                sys.exit(1)

            print('Service "{}" has been restarted.'.format(service_name))
        except Exception as e:
            print('Error restarting service: {}'.format(e))
            sys.exit(1)
    elif status == 'active':
        print('Service "{}" is already running.'.format(service_name))
    else:
        print('Unknown service status: {}'.format(status))

def execute_service_command(service_name, action, csb_version):
    if csb_version == 3:
        # For CSB version 3, use 'dzdo service' commands
        if action == 'start':
            command = 'dzdo service {0} start'.format(service_name)
        elif action == 'stop':
            command = 'dzdo service {0} stop'.format(service_name)
        elif action == 'status':
            try:
                result = subprocess.Popen(['service', service_name, 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error_output = result.communicate()
                
                if "running" in output.decode(default_encoding).lower():
                    print(output.decode(default_encoding))
                else:
                    print('{} is stopped'.format(service_name))
                return
            except Exception as e:
                print('Error executing command: {}'.format(e))
                sys.exit(1)
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
            try:
                result = subprocess.Popen(['dzdo', 'systemctl', 'status', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error_output = result.communicate()
                
                if result.returncode != 0:
                    error_output = error_output.strip().decode(default_encoding)
                    print('Error executing command: {}'.format(error_output))
                    sys.exit(1)
                
                print(output.decode(default_encoding))
                return
            except Exception as e:
                print('Error executing command: {}'.format(e))
                sys.exit(1)
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
            error_output = error_output.strip().decode(default_encoding)
            print('Error executing command: {}'.format(error_output))
            sys.exit(1)
        
        print('Service "{0}" {1}ed successfully.'.format(service_name, action))
    except Exception as e:
        print('Error executing command: {}'.format(e))
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        # If one argument is passed, assume it's script 1
        if len(sys.argv) != 2:
            print('Usage: ./DMZ.py <service_name>')
            sys.exit(1)

        service_name = sys.argv[1]
        csb_version = get_csb_version()

        restart_service_if_inactive(service_name, csb_version)
    elif len(sys.argv) == 3:
        # If two arguments are passed, assume it's script 2
        service_name = sys.argv[1]
        action = sys.argv[2].lower()  # Action: start, stop, restart, status
        csb_version = get_csb_version()

        execute_service_command(service_name, action, csb_version)
    else:
        print('Usage: \nFor Script 1: ./DMZ.py <service_name>\nFor Script 2: ./DMZ.py <service_name> <action>')
        sys.exit(1)
