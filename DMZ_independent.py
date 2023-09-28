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

def check_service_status(service_name):
    try:
        result = subprocess.Popen(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = result.communicate()
        return output.strip()  # Return the status (active or inactive)
    except Exception as e:
        print('Error checking service status: {}'.format(e))
        sys.exit(1)

def restart_service_if_inactive(service_name, csb_version):
    status = check_service_status(service_name)
    if status == 'inactive':
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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ./DMZ.py <service_name>')
        sys.exit(1)

    service_name = sys.argv[1]
    csb_version = get_csb_version()

    restart_service_if_inactive(service_name, csb_version)
