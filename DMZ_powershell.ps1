# Define a function to get the CSB version
function Get-CsbVersion {
    try {
        $result = & csb version 2>&1
        $csbVersion = [int]($result -split '\.')[0]
        return $csbVersion
    } catch {
        Write-Host "Error getting CSB version: $_"
        exit 1
    }
}

# Define a function to check the service status
function Check-ServiceStatus($serviceName) {
    try {
        $status = Get-Service $serviceName | Select-Object -ExpandProperty Status
        return $status
    } catch {
        Write-Host "Error checking service status: $_"
        exit 1
    }
}

# Define a function to restart the service if it is inactive
function Restart-ServiceIfInactive($serviceName, $csbVersion) {
    $status = Check-ServiceStatus $serviceName
    if ($status -eq "Stopped") {
        try {
            if ($csbVersion -eq 3) {
                # For CSB version 3, use 'dzdo service' commands
                & dzdo service $serviceName stop
                & dzdo service $serviceName start
            } elseif ($csbVersion -eq 4 -or $csbVersion -eq 8) {
                # For CSB versions 4 and 8, use 'dzdo systemctl' commands
                & dzdo systemctl stop $serviceName
                & dzdo systemctl start $serviceName
            } else {
                Write-Host "Unsupported CSB version."
                exit 1
            }

            Write-Host "Service ""$serviceName"" has been restarted."
        } catch {
            Write-Host "Error restarting service: $_"
            exit 1
        }
    } elseif ($status -eq "Running") {
        Write-Host "Service ""$serviceName"" is already running."
    } else {
        Write-Host "Unknown service status: $status"
    }
}

if ($args.Length -ne 1) {
    Write-Host "Usage: .\DMZ.ps1 <service_name>"
    exit 1
}

$serviceName = $args[0]
$csbVersion = Get-CsbVersion

Restart-ServiceIfInactive $serviceName $csbVersion
