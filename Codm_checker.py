#!/usr/bin/env python3
"""
KAI TWEAK'S — CODM / Garena Server Checker
Check status, ping, and region servers
"""

import requests
import time
import sys

SERVERS = {
    'Asia': 'https://codm-asia.garena.com',
    'NA': 'https://codm-na.garena.com',
    'EU': 'https://codm-eu.garena.com',
    'Global': 'https://www.callofduty.com/mobile'
}

def check_server(name, url):
    print(f"\n🔍 Checking {name}...")
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        ms = round((time.time() - start) * 1000)
        
        if r.status_code == 200:
            print(f"✅ {name} ONLINE • Ping: {ms}ms")
            return True
        else:
            print(f"⚠️  {name} Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} OFFLINE / Error: {str(e)[:40]}")
        return False

def main():
    print("="*45)
    print("   KAI TWEAK'S — CODM CHECKER")
    print("="*45)
    print(f"Time: {time.ctime()}")
    print()

    online = 0
    for name, url in SERVERS.items():
        if check_server(name, url):
            online += 1

    print("\n" + "="*45)
    print(f"Result: {online}/{len(SERVERS)} Servers Online")
    if online == len(SERVERS):
        print("✅ ALL SERVERS ONLINE — Ready to Play!")
    elif online > 0:
        print("⚠️  Some servers down — try another region")
    else:
        print("❌ All servers offline / No internet")
    print("="*45)

if __name__ == "__main__":
    main()
  
