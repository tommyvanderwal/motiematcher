#!/usr/bin/env python3
"""
Open screenshots automatically for LLM inspection - NO USER INPUT REQUIRED
"""

import os
import subprocess
import time

def open_screenshots_automatically():
    """Open recent screenshots automatically without any user input"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ No screenshots directory")
        return

    # Get all screenshots and sort by modification time (newest first)
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(screenshots_dir, x)), reverse=True)

    if not all_files:
        print("❌ No screenshots found")
        return

    print(f"🖼️  Opening {len(all_files)} screenshots automatically...")
    print("As LLM, I will examine each screenshot to verify the test results")

    # Open screenshots one by one with delays
    for i, filename in enumerate(all_files[:10], 1):  # Open first 10 most recent
        filepath = os.path.join(screenshots_dir, filename)
        print(f"📸 Opening screenshot {i}: {filename}")

        try:
            # Open with default Windows viewer
            subprocess.run(["start", filepath], shell=True, check=True)
            # Wait 3 seconds between screenshots so they can be viewed
            time.sleep(3)
        except Exception as e:
            print(f"❌ Could not open {filename}: {e}")

    print("\n✅ All screenshots opened automatically for inspection")
    print("LLM will now analyze the visual content...")

if __name__ == "__main__":
    open_screenshots_automatically()