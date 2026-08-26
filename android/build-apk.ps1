$ErrorActionPreference = 'Stop'
Write-Host 'MSP Local AI Agent Android - APK build' -ForegroundColor Cyan
if (-not (Get-Command gradle -ErrorAction SilentlyContinue)) {
    throw 'Gradle is not in PATH. Open the project in Android Studio, or install Gradle 9.5+ and rerun this script.'
}
if (-not $env:ANDROID_HOME -and -not $env:ANDROID_SDK_ROOT) {
    Write-Warning 'ANDROID_HOME/ANDROID_SDK_ROOT is not set. Gradle may still locate the SDK through local.properties if Android Studio configured it.'
}
gradle :app:assembleDebug
if ($LASTEXITCODE -ne 0) { throw 'Gradle build failed.' }
$apk = Join-Path $PSScriptRoot 'app\build\outputs\apk\debug\app-debug.apk'
if (-not (Test-Path $apk)) { throw "Build completed but APK was not found at $apk" }
Write-Host "APK ready: $apk" -ForegroundColor Green
Get-FileHash $apk -Algorithm SHA256 | Format-List
