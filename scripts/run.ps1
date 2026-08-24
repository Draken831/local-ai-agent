$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if(-not (Test-Path ".\.venv\Scripts\python.exe")) {
    & "$PSScriptRoot\setup.ps1"
}
if(-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment is missing after setup."
}

& ".\.venv\Scripts\python.exe" -m msp_agent.cli
