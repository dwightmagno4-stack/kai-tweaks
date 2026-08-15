#!/system/bin/sh
# KAI TWEAK'S — Garena Checker Uninstaller
# Clean reset • No leftover props

MODDIR=${0%/*}

echo "====================================="
echo "   KAI TWEAK'S — Uninstalling..."
echo "   GARENA CHECKER                   "
echo "====================================="

# Reset system props
setprop debug.hwui.renderer ""
setprop debug.hwui.use_vulkan ""
setprop debug.display.fps ""
setprop debug.sf.max_frame_rate ""
setprop debug.game.mode ""
setprop debug.perf.game_priority ""
setprop net.tcp.no_delay ""
setprop net.tcp_sack ""

# Remove logs
rm -f "$MODDIR/gchecker.log"
rm -rf "$MODDIR/logs"

echo ""
echo "✅ All props reset"
echo "✅ Logs cleared"
echo "✅ Garena Checker removed"
echo "====================================="
