#!/usr/bin/env python3
"""Simple script to verify the local FastAPI server"""

import urllib.request
import urllib.error
import json

def check_endpoint(path: str = "/"):
    url = f"http://127.0.0.1:8001{path}"
    try:
        with urllib.request.urlopen(url) as response:
            status = response.status
            body = response.read(500).decode("utf-8", errors="ignore")
            print(f"GET {path} -> {status}")
            print(body[:200])
            return status
    except urllib.error.HTTPError as err:
        print(f"HTTP error for {path}: {err.code}")
        return err.code
    except urllib.error.URLError as err:
        print(f"Failed to reach server for {path}: {err}")
        return None

if __name__ == "__main__":
    status_root = check_endpoint("/")
    if status_root == 200:
        print("Root endpoint reachable.")
    else:
        print("Root endpoint failed.")
