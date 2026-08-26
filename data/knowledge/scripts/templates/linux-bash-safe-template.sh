#!/usr/bin/env bash
set -u
LOG="/var/log/msp-agent-script.log"
log(){ echo "$(date -Is) $*" | tee -a "$LOG"; }
log "Script started"
# diagnostics first; avoid destructive actions unless approved
