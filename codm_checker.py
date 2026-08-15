#!/usr/bin/env python3
"""
KAI TWEAK'S — CODM / Garena Server Checker
Check status, ping, and official pages
"""

import requests
import time
import socket

# Working URLs & IPs
SERVERS = {
    'Garena Main': 'https://www.garena.com',
    'CODM Official': 'https://www.callofduty.com/mobile',
    'Garena CODM News': 'https://codm.garena.com/news',
    'Asia (Ping)': '1.1.1.1',  # Test region connectivity
}

def check_http(name, url):
    print(f"\n🔍 Checking {name}...")
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        ms = round((time.time() - start) * 1000)
        
        if r.status_code == 200:
            print(f"✅ {name} ONLINE • Ping: {ms}ms")
            return True
        else:
            print(f"⚠️  {name} Status Code: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} OFFLINE / Error: {str(e)[:50]}")
        return False

def check_ping(name, host):
    print(f"\n📶 Pinging {name}...")
    try:
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, 53))  # DNS port = quick test
        ms = round((time.time() - start) * 1000)
        s.close()
        print(f"✅ {name} CONNECTED • Ping: {ms}ms")
        return True
    except Exception as e:
        print(f"❌ {name} UNREACHABLE")
        return False

def main():
    print("="*45)
    print("   KAI TWEAK'S — CODM CHECKER")
    print("="*45)
    print(f"Time: {time.ctime()}")
    print()

    online = 0
    total = 0

    # Check web pages
    for name, url in SERVERS.items():
        total += 1
        if '.' in url and not url.replace('.','').isdigit():
            if check_http(name, url):
                online += 1
        else:
            if check_ping(name, url):
                online += 1

    print("\n" + "="*45)
    print(f"Result: {online}/{total} Services Online")
    if online == total:
        print("✅ ALL ONLINE — Ready to Play!")
    elif online > 0:
        print("⚠️  Some issues — check your connection")
    else:
        print("❌ No connection — check internet")
    print("="*45)

if __name__ == "__main__":
    main()
  
