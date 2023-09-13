# Define variables
[string]$suname = "integration.eyeshare"
[string]$pwd = "Eyeshare@123456"
[string]$snowURL = "https://cssnowptasoap.service-now.com"
[string]$Sproxy_uname = "GBLADHEDANI\s_HS_Automation_P"
[string]$proxy_pwd = "%sv_pass%!"
[string]$proxyURL = "http://proxy.hedani.net:8080"

# Convert $pwd to SecureString
[SecureString]$pwdSecure = $pwd | ConvertTo-SecureString -AsPlainText -Force

# Create PSCredential object
[PSCredential]$scred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $suname, $pwdSecure

# Convert $proxy_pwd to SecureString
[SecureString]$proxy_pwdSecure = $proxy_pwd | ConvertTo-SecureString -AsPlainText -Force

# Create $proxy_cred PSCredential object
[PSCredential]$proxy_cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Sproxy_uname, $proxy_pwdSecure

# Define RFC variables
[string]$rfc_shortdesc = "Install the EcoSystem Agent via SPUDS on the following Windows Server(s) in ROW Regions"
[string]$rfc_description = @"

%rfc_description
Downstream Impact - NA
Change Contact - DD Group CTO HDCS HPO Automation Support

"@
[string]$rfc_template = "EcoSystem Agent SPUDS Install Template - Windows (ROW)"
$rfc_start_date = (Get-Date).AddMinutes(-119) | Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$rfc_end_date = (Get-Date).AddMinutes(100) | Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$work_end_date = (Get-Date).AddMinutes(99) | Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$actual_start_date = (Get-Date).AddMinutes(-332) | Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$actual_end_date = (Get-Date).AddMinutes(-331) | Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# Description
$description = @"
$rfc_description
"@

# Set the security protocol
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Function RFC_Create
Function RFC_Create {
    $URL = "$($snowURL)/api/now/table/change_request"

    $headers = @{
        "Content-Type" = "application/json"
        "Accept" = "application/json"
    }

    $payload = @{
        "_requester_group" = "ae31ad7f4f11a6c03031401f0310c722"
        "type" = ""
        "ci_class" = "cmdb_ci_win_server"
        "u_work_activity" = "Performance Tuning"
        "u_source_system" = "eyeShare"
        "u_support_group" = "0c582c4a4f31b2c86dc5401f0310c7f0"
        "requested_by" = "integration.eyeshare"
        "u_dr_environment" = "Yes"
        "u_environment" = "PROD"
        "u_template_name" = "cd6ca6a0db83b814005b5c88f4961936"
        "u_impacted_regions_list" = "018bfaf03c638580f9f06fd93df64cd6,558bfaf03c638580f9f06fd93df64cd7,1d8bfaf03c638580f9f06fd93df64cd6"
        "_impacted_countries" = "9f57e16de0390100e1c5111c6bcf8c84,798761ade0390100e1c5111c6bcf8c99,0a67296de0390100e1c5111c6bcf8c"
        "u_all_business_areas_impacted" = "false"
        "_impacted_business_areas_list" = "24fb94598735a150486cc8090cbb3533"
        "u_activity_type" = "2"
        "cmdb_ci" = "cmdb_ci_win_server"
        "start_date" = "$rfc_start_date"
        "end_date" = "$rfc_end_date"
        "short_description" = "$rfc_shortdesc"
        "description" = "$description"
        "u_test_evidence" = "Linked"
        "test_plan" = "https://atlas.apps.csintra.net/confluence/display/TCHLDS/spuds#spuds-testservers.py"
        "backout_plan" = "https://atlas.apps.csintra.net/confluence/display/TCHLDS/spuds#spuds-Uninstall(use-e)"
    }
}

# RFC_Create
$get_data = RFC_Create
$get_rfc_number = $get_data.number
$get_sys_id = $get_data.sys_id

# Function RFC_CIUpdate
Function RFC_CIUpdate {
    $rfc = "$get_rfc_number"
    $CI_Name = "gbwp9009744"
    $URL = "$($snowURL)/api/now/table/task_ci"

    $headers = @{
        "Content-Type" = "application/json"
        "Accept" = "application/json"
    }

    $payload = @{
        "task" = $rfc
        "ci item" = $CI_Name
    }

    $response = Invoke-RestMethod -Headers $headers -Method Post -Body ($payload | ConvertTo-Json) -Uri $URL -Credential $scred -Proxy $proxyURL -ProxyCredential $proxy_cred
}

RFC_CIUpdate

# Function RFC_Schedule
Function RFC_Schedule {
    $rfc_sys_id = "$get_sys_id"
    $URL = "$($snowURL)/api/now/table/change_request/$($rfc_sys_id)"

    $headers = @{
        "Content-Type" = "application/json"
        "Accept" = "application/json"
    }

    $payload = @{
        "_implementation_start" = "$rfc_start_date"
        "work_end" = "$work_end_date"
        "u_source_system" = "eyeShare"
        "implementer" = "integration.eyeshare"
        "u_change_state" = "implementer confirmation"
    }

    $response = Invoke-RestMethod -Headers $headers -Method Put -Body ($payload | ConvertTo-Json) -Uri $URL -Credential $scred -Proxy $proxyURL -ProxyCredential $proxy_cred

    $payload = @{
        "description" = "$description"
        "u_reason_for_no_cs_sdf" = "For remediation of Lager installation"
    }

    $response = Invoke-RestMethod -Headers $headers -Method Put -Body ($payload | ConvertTo-Json) -Uri $URL -Credential $scred -Proxy $proxyURL -ProxyCredential $proxy_cred
}

RFC_Schedule
$get_rfc_number.Trim()

# Function RFC_requesterReview
function RFC_requesterReview {
    $rfc_sys_id = "$get_sys_id"
    $URL = "$($snowURL)/api/now/table/change_request/$($rfc_sys_id)"

    $headers = @{
        "Content-Type" = "application/json"
        "Accept" = "application/json"
    }

    $payload = @{
        "work_notes" = "RFC implementation started"
    }
}

RFC_requesterReview
