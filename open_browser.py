#!/usr/bin/env python3
"""
Script to open browser to web app
"""

import webbrowser
import time

def main():
    url = "http://127.0.0.1:8001"
    print(f"Opening browser to {url}")
    webbrowser.open(url)
    time.sleep(2)  # Give browser time to open
    print("Browser opened successfully")

if __name__ == "__main__":
    main()