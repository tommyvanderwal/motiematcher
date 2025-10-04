#!/usr/bin/env python3
"""
Simple Web App Test - Just check if the page loads
"""

import time
import webbrowser
import subprocess
import sys
import os

def test_web_app_loading():
    """Test if the web app actually loads in browser"""

    print("🧪 Testing Web App Loading")
    print("=" * 40)

    # Start web app
    print("🚀 Starting web app...")
    main_file = "app/main_improved.py"
    if not os.path.exists(main_file):
        print(f"❌ Main file not found: {main_file}")
        return

    try:
        cmd = [sys.executable, main_file]
        process = subprocess.Popen(cmd)
        print("✅ Web app process started")
        time.sleep(3)  # Wait for startup

        # Test HTTP response
        print("🌐 Testing HTTP response...")
        import urllib.request
        try:
            response = urllib.request.urlopen("http://127.0.0.1:51043", timeout=5)
            if response.status == 200:
                content = response.read().decode('utf-8')
                print("✅ HTTP 200 - Web app responds")
                if "Start Stemming" in content:
                    print("✅ Page contains expected content")
                else:
                    print("⚠️  Page loaded but content unexpected")
                    print(f"Content length: {len(content)} chars")
            else:
                print(f"❌ HTTP {response.status}")
        except Exception as e:
            print(f"❌ HTTP request failed: {e}")

        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open("http://127.0.0.1:51043")
        print("✅ Browser opened")

        # Wait for user to check
        print("\n" + "=" * 40)
        print("🎯 CHECK YOUR BROWSER NOW!")
        print("Does the page show:")
        print("- A 'Start Stemming' button?")
        print("- Proper styling?")
        print("- No errors?")
        print("=" * 40)

        input("Press Enter when you've checked the browser...")

        # Stop web app
        print("🛑 Stopping web app...")
        process.terminate()
        process.wait()
        print("✅ Test completed")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_web_app_loading()