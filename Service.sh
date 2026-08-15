#!/system/bin/sh
# KAI TWEAK'S — Garena Checker Service
# Auto-start on boot • Non-root • No reboot needed

MODDIR=${0%/*}
LOG="$MODDIR/gchecker.log"

# Log function
log() { echo "[$(date +%H:%M:%S)] $1" >> "$LOG"; }

log "=== Garen Checker Service Started ==="

# Wait for boot complete
sleep 10

# Set Garena/CODM optimizations
setprop debug.hwui.renderer skia_gl
setprop debug.hwui.use_vulkan 0
setprop debug.display.fps 60
setprop debug.sf.max_frame_rate 60
setprop debug.game.mode 1
setprop debug.perf.game_priority 1
setprop net.tcp.no_delay 1
setprop net.tcp_sack 1

log "System props applied"

# Keep process alive (non-root safe)
while true; do
    # Check internet every 5 min
    ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        log "Network: CONNECTED"
    else
        log "Network: DISCONNECTED"
    fi
    sleep 300
done
