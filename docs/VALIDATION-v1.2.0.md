# Validation — v1.2.0

Validated before promotion to `main`:

- GUI is the default interface.
- `msp-agent` launches `msp_agent.launcher`, which launches the GUI unless `--cli` is explicitly supplied.
- `scripts/run.ps1` launches the GUI-default launcher.
- Explicit CLI remains available through `scripts/run-cli.ps1` and `msp-agent --cli`.
- Cloud-first provider order remains `cloud,local`.
- Cloud web search remains enabled for research routes; local pre-cloud search remains disabled.
- 97 curated quick-answer rules load successfully from eight verifiable text bundle parts.
- Natural-variation quick-answer smoke tests passed.
- 13 Python modules compiled successfully.
- PowerShell parser-trap static checks returned zero matches.

Local distribution package SHA-256:
`d20acc29e961d527580826889cae80dd1ae25ca27d9998dda1ae67a4446352d6`

Installer SHA-256:
`ce80ff72dc7dc834bb09e389ea5416b19d9b0e05d0ebe16bb9bc66bfac31ce75`
