# Validation — v1.1.1

The cloud-first correction was validated before publication.

- Provider order defaults to `cloud,local`.
- Cloud web search is enabled for research routes.
- Automatic local SearXNG execution before cloud is disabled.
- Automatic local quick-answer execution before cloud is disabled.
- Cloud retries default to `0` for speed.
- Cloud circuit breaker opens after `2` consecutive failures by default.
- 12 Python modules compiled successfully.
- PowerShell `$Variable:` parser-trap scan: 0 unsafe matches.
- PowerShell `Test-Path ... -and/-or` parser-trap scan: 0 unsafe matches.
- UTF-8 BOM scan: 0 generated text files with BOM.

This validates static/runtime routing behavior in the build environment. Windows-specific prerequisite installation and live cloud credentials still require validation on the target Windows machine.
