param([Parameter(Mandatory=$true)][string]$FilePath,[string]$TimestampUrl="http://timestamp.digicert.com")
$SignTool=& "$PSScriptRoot\Find-SignTool.ps1"
if(-not $SignTool){ throw "SignTool not found. Install Windows SDK." }
& $SignTool sign /a /fd SHA256 /tr $TimestampUrl /td SHA256 $FilePath
& $SignTool verify /pa /v $FilePath
