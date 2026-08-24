$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Refresh-ProcessPath {
    $machine = [Environment]::GetEnvironmentVariable("Path","Machine")
    $user = [Environment]::GetEnvironmentVariable("Path","User")
    $env:Path = "$machine;$user"
}

function Test-PythonExe($Path) {
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
    if($pf86){ $candidates += @("$pf86\Python312\python.exe","$pf86\Python311\python.exe") }
    foreach($c in $candidates){ if(Test-PythonExe $c){ return $c } }
    try {
        $p = py -3 -c "import sys; print(sys.executable)" 2>$null
        if($LASTEXITCODE -eq 0 -and $p -and (Test-PythonExe $p.Trim())){ return $p.Trim() }
    } catch {}
    try {
        $cmd = Get-Command python -ErrorAction Stop
        if($cmd.Source -and (Test-PythonExe $cmd.Source)){ return $cmd.Source }
    } catch {}
    throw "Python 3.10+ was not found."
}

if(-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Warning "Created .env from .env.example. Set CLOUD_API_KEY before expecting cloud inference."
}

$PythonExe = Find-Python
Write-Host "Using Python: $PythonExe" -ForegroundColor Green

if((Test-Path ".\.venv") -and -not (Test-Path ".\.venv\Scripts\python.exe")) {
    Remove-Item ".\.venv" -Recurse -Force
}
if(-not (Test-Path ".\.venv\Scripts\python.exe")) {
    & $PythonExe -m venv ".\.venv"
    if($LASTEXITCODE -ne 0){ throw "Virtual environment creation failed." }
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
if($LASTEXITCODE -ne 0){ throw "pip upgrade failed." }

& ".\.venv\Scripts\python.exe" -m pip install -e .
if($LASTEXITCODE -ne 0){ throw "Agent package install failed." }

$pythonFiles = Get-ChildItem ".\src\msp_agent\*.py"
foreach($file in $pythonFiles) {
    & ".\.venv\Scripts\python.exe" -m py_compile $file.FullName
    if($LASTEXITCODE -ne 0){ throw "Python validation failed: $($file.Name)" }
}

Write-Host "Setup complete. Cloud is primary when CLOUD_API_KEY is configured." -ForegroundColor Green

# Create/update a Desktop shortcut for the default GUI.
try {
    $desktop = [Environment]::GetFolderPath("Desktop")
    if($desktop){
        $shortcutPath = Join-Path $desktop "MSP AI Agent.lnk"
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ProjectRoot\scripts\run.ps1`""
        $shortcut.WorkingDirectory = $ProjectRoot
        $shortcut.Description = "MSP AI Agent - Cloud First GUI"
        $shortcut.Save()
        Write-Host "Desktop shortcut created: $shortcutPath" -ForegroundColor Green
    }
}catch{
    Write-Warning "Could not create Desktop shortcut: $($_.Exception.Message)"
}
