$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=== Cloud-first AI Agent health check ===" -ForegroundColor Cyan

if(Test-Path ".env") {
    $cloudKeyConfigured = Select-String -Path ".env" -Pattern '^\s*CLOUD_API_KEY\s*=\s*.+$' -Quiet
    Write-Host "Cloud API key configured: $cloudKeyConfigured"
} else {
    Write-Warning ".env is missing."
}

try {
    $ollama = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
    Write-Host "Local Ollama reachable: True" -ForegroundColor Green
} catch {
    Write-Host "Local Ollama reachable: False (acceptable while cloud is healthy)" -ForegroundColor Yellow
}

if(Test-Path ".\.venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" -c "from pathlib import Path; from msp_agent.config import load_settings; from msp_agent.router import choose_model; from msp_agent.llm import AIClient; s=load_settings(Path.cwd()); r=choose_model('health check',s); c=AIClient(s,r); print(c.health())"
} else {
    Write-Warning "Python venv missing. Run .\scripts\setup.ps1"
}
