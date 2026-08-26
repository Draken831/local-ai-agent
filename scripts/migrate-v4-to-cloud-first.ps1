[CmdletBinding()]
param(
    [string]$TargetRoot = "C:\Projects\msp-local-ai-agent-fresh"
)

$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent $PSScriptRoot

if(-not (Test-Path $TargetRoot)){
    throw "Target project does not exist: $TargetRoot"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $TargetRoot "data\runtime\cloud-first-migration-backup-$stamp"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$replace = @(
    "pyproject.toml",
    "src\msp_agent\__init__.py",
    "src\msp_agent\config.py",
    "src\msp_agent\router.py",
    "src\msp_agent\llm.py",
    "src\msp_agent\cli.py",
    "src\msp_agent\gui.py",
    "src\msp_agent\launcher.py",
    "src\msp_agent\quick_answers.py",
    "src\msp_agent\learning.py",
    "src\msp_agent\doc_indexer.py",
    "data\brain\quick_answers.bundle",
    "scripts\setup.ps1",
    "scripts\run.ps1",
    "scripts\run-cli.ps1",
    "scripts\run-gui.ps1",
    "scripts\healthcheck.ps1",
    "Start-MSP-AI-Agent.cmd"
)

foreach($relative in $replace){
    $source = Join-Path $SourceRoot $relative
    $target = Join-Path $TargetRoot $relative

    if(-not (Test-Path $source)){
        throw "Correction package is missing: $relative"
    }

    if(Test-Path $target){
        $backup = Join-Path $backupRoot $relative
        $backupDir = Split-Path -Parent $backup
        if($backupDir){ New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }
        Copy-Item $target $backup -Force
    }

    $targetDir = Split-Path -Parent $target
    if($targetDir){ New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
    Copy-Item $source $target -Force
}

$envFile = Join-Path $TargetRoot ".env"
$example = Join-Path $SourceRoot ".env.example"

if(-not (Test-Path $envFile)){
    Copy-Item $example $envFile -Force
}else{
    Copy-Item $envFile (Join-Path $backupRoot ".env") -Force

    $current = Get-Content $envFile -Raw
    $exampleLines = Get-Content $example

    foreach($line in $exampleLines){
        if($line -match '^\s*([A-Z0-9_]+)='){
            $name = $Matches[1]
            if($current -notmatch "(?m)^\s*$([regex]::Escape($name))\s*="){
                Add-Content -Path $envFile -Value $line
                $current += "`r`n$line"
            }
        }
    }

    function Set-EnvValue([string]$Name,[string]$Value){
        $text = Get-Content $envFile -Raw
        $pattern = "(?m)^\s*$([regex]::Escape($Name))\s*=.*$"
        $replacement = "$Name=$Value"
        if($text -match $pattern){
            $text = [regex]::Replace($text,$pattern,$replacement)
        }else{
            $text += "`r`n$replacement`r`n"
        }
        $enc = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($envFile,$text,$enc)
    }

    # These values define the architecture. Enforce them during v4 -> v1.3.0 migration.
    Set-EnvValue "AI_PROVIDER_ORDER" "cloud,local"
    Set-EnvValue "CLOUD_AI_ENABLED" "true"
    Set-EnvValue "CLOUD_WEB_SEARCH_ENABLED" "true"
    Set-EnvValue "ONLINE_FIRST_MODE" "false"
    Set-EnvValue "LOCAL_FALLBACK_ENABLED" "true"
    Set-EnvValue "CLOUD_RETRIES" "0"
    Set-EnvValue "CLOUD_CIRCUIT_BREAKER_FAILURES" "2"
}

Set-Location $TargetRoot

if(Test-Path ".\.venv\Scripts\python.exe"){
    & ".\.venv\Scripts\python.exe" -m pip install -e .
    if($LASTEXITCODE -ne 0){ throw "pip reinstall failed." }

    Get-ChildItem ".\src\msp_agent\*.py" | ForEach-Object {
        & ".\.venv\Scripts\python.exe" -m py_compile $_.FullName
        if($LASTEXITCODE -ne 0){
            throw "Python compile validation failed: $($_.Name)"
        }
    }
}

Write-Host "Cloud-first migration complete." -ForegroundColor Green
Write-Host "Backup: $backupRoot"
Write-Host "Architecture enforced: cloud -> local"
Write-Host "Edit $envFile and set CLOUD_API_KEY if it is blank."
Write-Host "Then run: .\scripts\healthcheck.ps1"
Write-Host "Start the GUI with: .\scripts\run.ps1"
