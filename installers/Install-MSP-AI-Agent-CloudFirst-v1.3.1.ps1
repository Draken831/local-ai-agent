<#
MSP AI Agent - Cloud First / Local Fallback 1.3.1
Bootstrap installer/updater for the GitHub-published project.

Behavior:
- Downloads the current main branch from GitHub.
- Preserves an existing .env unless -ForceReplace is used.
- Enforces strict cloud-first routing flags.
- Installs Python only when requested and missing.
- Installs Ollama only when -InstallLocalFallback is requested.
#>

[CmdletBinding()]
param(
    [string]$TargetRoot = "C:\Projects\msp-local-ai-agent-fresh",
    [string]$RepositoryZipUrl = "https://github.com/Draken831/local-ai-agent/archive/refs/heads/main.zip",
    [switch]$ForceReplace,
    [switch]$InstallPrereqs,
    [switch]$InstallLocalFallback
)

$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

function Refresh-ProcessPath {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Test-PythonExe([string]$Path) {
    if(-not $Path -or -not (Test-Path $Path)){ return $false }
    try {
        $out = & $Path -c "import sys; print(sys.version_info[0])" 2>$null
        return ($LASTEXITCODE -eq 0 -and $out -and $out[0] -eq "3")
    } catch { return $false }
}

function Find-Python {
    Refresh-ProcessPath
    $pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )
    if($pf86){
        $candidates += @("$pf86\Python312\python.exe", "$pf86\Python311\python.exe")
    }
    foreach($candidate in $candidates){
        if(Test-PythonExe $candidate){ return $candidate }
    }
    try {
        $cmd = Get-Command python -ErrorAction Stop
        if($cmd.Source -and (Test-PythonExe $cmd.Source)){ return $cmd.Source }
    } catch {}
    return $null
}

function Winget-Install([string]$Id, [string]$Name) {
    if(-not (Get-Command winget -ErrorAction SilentlyContinue)){
        throw "winget is not available. Install $Name manually."
    }
    & winget install --id $Id -e --accept-source-agreements --accept-package-agreements
    if($LASTEXITCODE -ne 0){
        throw "winget failed installing $Name ($Id)."
    }
    Refresh-ProcessPath
}

function Write-Utf8NoBom([string]$Path, [string]$Text) {
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $enc)
}

function Set-EnvValue([string]$File, [string]$Name, [string]$Value) {
    $text = if(Test-Path $File){ Get-Content $File -Raw } else { "" }
    $pattern = "(?m)^\s*$([regex]::Escape($Name))\s*=.*$"
    $replacement = "$Name=$Value"
    if($text -match $pattern){
        $text = [regex]::Replace($text, $pattern, $replacement)
    } else {
        if($text -and -not $text.EndsWith("`n")){ $text += "`r`n" }
        $text += "$replacement`r`n"
    }
    Write-Utf8NoBom $File $text
}

function Copy-Tree([string]$Source, [string]$Destination) {
    if(-not (Test-Path $Destination)){
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    }
}

$python = Find-Python
if(-not $python -and $InstallPrereqs){
    Winget-Install "Python.Python.3.12" "Python 3.12"
    $python = Find-Python
}
if(-not $python){
    throw "Python 3.10+ was not found. Install Python 3.12 or rerun with -InstallPrereqs."
}

if($InstallLocalFallback -and -not (Get-Command ollama -ErrorAction SilentlyContinue)){
    Winget-Install "Ollama.Ollama" "Ollama"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$tempRoot = Join-Path $env:TEMP "msp-ai-cloudfirst-$stamp-$([guid]::NewGuid().ToString('N'))"
$zipPath = "$tempRoot.zip"
$extractRoot = "$tempRoot-extract"
New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null

Write-Host "Downloading cloud-first 1.3.1 source..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $RepositoryZipUrl -OutFile $zipPath -UseBasicParsing
Expand-Archive -Path $zipPath -DestinationPath $extractRoot -Force

$sourceRoot = Get-ChildItem -LiteralPath $extractRoot -Directory | Select-Object -First 1
if(-not $sourceRoot){ throw "Downloaded repository archive did not contain a source directory." }

$envBackup = $null
if((Test-Path $TargetRoot) -and (Test-Path (Join-Path $TargetRoot ".env")) -and -not $ForceReplace){
    $envBackup = Join-Path $env:TEMP "msp-ai-env-$stamp-$([guid]::NewGuid().ToString('N')).bak"
    Copy-Item (Join-Path $TargetRoot ".env") $envBackup -Force
}

if($ForceReplace -and (Test-Path $TargetRoot)){
    Remove-Item $TargetRoot -Recurse -Force
}

Copy-Tree $sourceRoot.FullName $TargetRoot

$envFile = Join-Path $TargetRoot ".env"
if($envBackup){
    Copy-Item $envBackup $envFile -Force
    Remove-Item $envBackup -Force -ErrorAction SilentlyContinue
}elseif(-not (Test-Path $envFile)){
    Copy-Item (Join-Path $TargetRoot ".env.example") $envFile -Force
}

# Enforce architecture-critical settings.
Set-EnvValue $envFile "AI_PROVIDER_ORDER" "cloud,local"
Set-EnvValue $envFile "CLOUD_AI_ENABLED" "true"
Set-EnvValue $envFile "CLOUD_WEB_SEARCH_ENABLED" "true"
Set-EnvValue $envFile "LOCAL_SEARXNG_PRECONTEXT" "false"
# Legacy compatibility: explicitly neutralize old pre-cloud SearXNG flag.
Set-EnvValue $envFile "ONLINE_FIRST_MODE" "false"
Set-EnvValue $envFile "LOCAL_FALLBACK_ENABLED" "true"
Set-EnvValue $envFile "CLOUD_RETRIES" "0"
Set-EnvValue $envFile "CLOUD_CIRCUIT_BREAKER_FAILURES" "2"

Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
Remove-Item $extractRoot -Recurse -Force -ErrorAction SilentlyContinue

Set-Location $TargetRoot
& ".\scripts\setup.ps1"
if($LASTEXITCODE -ne 0){ throw "Project setup failed." }

Write-Host ""
Write-Host "Cloud-first 1.3.1 install/update complete." -ForegroundColor Green
Write-Host "Target: $TargetRoot"
Write-Host "Provider priority: cloud -> local"
Write-Host "Set CLOUD_API_KEY in: $envFile"
Write-Host "Validate: .\scripts\healthcheck.ps1"
Write-Host "Start GUI: .\scripts\run.ps1"
