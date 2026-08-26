# Validation — v1.3.0

Validated before GitHub publication on 2026-08-26.

## Windows

- Python modules compiled: PASS
- Cloud-first provider order (`cloud,local`): PASS
- Cloud connect/read timeouts (3s / 15s): PASS
- Cloud retries default (0): PASS
- GUI import/default launcher: PASS
- Effective quick answers: 105
- Uploaded local quick-answer additions: 8
- Learning module/validation: PASS
- PowerShell unsafe `$Variable:` parser matches: 0
- Unsafe `Test-Path ... -and/-or` parser patterns: 0
- Secret scan: PASS
- Live `.env` committed: NO

## Android

- Java source files checked: 19
- Unbalanced Java braces: 0
- Cloud-first default: PASS
- Cloud chat/vision timeout: 15 seconds
- Local quick answers before normal cloud chat: NO
- Local Quick explicit path: YES
- Local SearXNG pre-context default: OFF
- Secret scan: PASS
- APK produced in this environment: NO

Android source remains buildable in Android Studio / Android SDK tooling; this environment does not contain the Android SDK required to produce a real APK.
