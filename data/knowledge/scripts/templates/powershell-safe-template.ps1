[CmdletBinding(SupportsShouldProcess=$true)]
param([string]$LogPath="C:\NSU\Script.log")
$ErrorActionPreference="Stop"
New-Item -ItemType Directory -Path (Split-Path $LogPath -Parent) -Force | Out-Null
function Write-Log($Message){ "$(Get-Date -Format s) $Message" | Tee-Object -FilePath $LogPath -Append }
Write-Log "Script started"
try {
    # diagnostics first
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    throw
}
