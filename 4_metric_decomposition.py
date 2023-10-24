def check_service_status(service_name, csb_version):
    try:
        if service_name in ('splunk', 'splunkagent'):
            # Handle Splunk and SplunkAgent separately
            result = subprocess.Popen(['/opt/splunk/agent/bin/splunk', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error_output = result.communicate()
            output = output.strip().decode()  # Decode the output

            if "is running" in output:
                return "active"
            else:
                return "inactive"
        elif csb_version in (4, 8):
            result = subprocess.Popen(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = result.communicate()
            return output.strip()  # Return the status (active or inactive)
        elif csb_version == 3:
            result = subprocess.Popen(['service', service_name, 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = result.communicate()

            if "running" in output.decode().lower():
                return "active"
            else:
                return "inactive"  # Return 'inactive' when the service is not running
        else:
            print('Unsupported CSB version.')
            sys.exit(1)

    except Exception as e:
        print('Error checking service status: {}'.format(e))
        sys.exit(1)
