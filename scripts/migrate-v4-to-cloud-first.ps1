[CmdletBinding()]
param([string]$TargetRoot = "C:\Projects\msp-local-ai-agent-fresh")
$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent $PSScriptRoot
if(-not (Test-Path $TargetRoot)){throw "Target project does not exist: $TargetRoot"}
$stamp=Get-Date -Format "yyyyMMdd-HHmmss"; $backupRoot=Join-Path $TargetRoot "data\runtime\cloud-first-migration-backup-$stamp"; New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$replace=@("pyproject.toml","src\msp_agent\__init__.py","src\msp_agent\config.py","src\msp_agent\router.py","src\msp_agent\llm.py","src\msp_agent\cli.py","src\msp_agent\gui.py","src\msp_agent\doc_indexer.py","scripts\setup.ps1","scripts\healthcheck.ps1")
foreach($relative in $replace){$source=Join-Path $SourceRoot $relative; $target=Join-Path $TargetRoot $relative; if(-not (Test-Path $source)){throw "Correction package is missing: $relative"}; if(Test-Path $target){$backup=Join-Path $backupRoot $relative; $backupDir=Split-Path -Parent $backup; if($backupDir){New-Item -ItemType Directory -Path $backupDir -Force | Out-Null}; Copy-Item $target $backup -Force}; $targetDir=Split-Path -Parent $target; if($targetDir){New-Item -ItemType Directory -Path $targetDir -Force | Out-Null}; Copy-Item $source $target -Force}
$envFile=Join-Path $TargetRoot ".env"; $example=Join-Path $SourceRoot ".env.example"
if(-not (Test-Path $envFile)){Copy-Item $example $envFile -Force}else{$current=Get-Content $envFile -Raw; $newLines=New-Object System.Collections.Generic.List[string]; Get-Content $example | ForEach-Object {$line=$_; if($line -match '^\s*([A-Z0-9_]+)='){$name=$Matches[1]; if($current -notmatch "(?m)^\s*$([regex]::Escape($name))\s*="){[void]$newLines.Add($line)}}}; if($newLines.Count -gt 0){Add-Content -Path $envFile -Value "`r`n# Added by cloud-first migration $stamp"; Add-Content -Path $envFile -Value $newLines}}
Set-Location $TargetRoot
if(Test-Path ".\.venv\Scripts\python.exe"){& ".\.venv\Scripts\python.exe" -m pip install -e .; if($LASTEXITCODE -ne 0){throw "pip reinstall failed."}; Get-ChildItem ".\src\msp_agent\*.py" | ForEach-Object {& ".\.venv\Scripts\python.exe" -m py_compile $_.FullName; if($LASTEXITCODE -ne 0){throw "Python compile validation failed: $($_.Name)"}}}
Write-Host "Cloud-first migration complete." -ForegroundColor Green
Write-Host "Backup: $backupRoot"
Write-Host "Edit $envFile and set CLOUD_API_KEY. Then run .\scripts\healthcheck.ps1"
