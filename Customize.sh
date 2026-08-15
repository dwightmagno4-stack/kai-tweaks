#!/system/bin/sh
# KAI TWEAK'S — Garena Checker Installer
# Version: 1.0

MODDIR=${0%/*}

ui_print "====================================="
ui_print "   KAI TWEAK'S — GARENA CHECKER      "
ui_print "   Installing...                     "
ui_print "====================================="
ui_print ""

# Set permissions
ui_print "Setting permissions..."
set_perm_recursive "$MODDIR" 0 0 0755 0644
set_perm "$MODDIR/service.sh" 0 0 0755
set_perm "$MODDIR/uninstall.sh" 0 0 0755

# Create log dir
mkdir -p "$MODDIR/logs"

ui_print ""
ui_print "✅ Install Complete!"
ui_print "   Run: python codm_checker.py"
ui_print "====================================="
