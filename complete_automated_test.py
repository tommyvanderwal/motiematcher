#!/usr/bin/env python3
"""
Complete automated test that opens browser and runs the smart test
"""

import webbrowser
import time
import os
import subprocess

def open_browser_and_test():
    """Open browser to the web app and run the smart test"""

    print("🌐 Opening browser to web app...")
    url = "http://127.0.0.1:8001"

    # Open browser
    webbrowser.open(url)
    time.sleep(3)  # Wait for browser to open

    # Run the smart test
    print("🚀 Running smart automated test...")
    result = subprocess.run(["python", "smart_test_improved.py"], capture_output=True, text=True)

    print("Test output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0

if __name__ == "__main__":
    success = open_browser_and_test()
    if success:
        print("✅ Complete automated test succeeded!")
    else:
        print("❌ Complete automated test failed!")