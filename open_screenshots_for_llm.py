#!/usr/bin/env python3
"""
Actually open the screenshots so I can SEE them as an LLM
"""

import os
import subprocess
import time

def open_screenshots_for_llm_inspection():
    """Open screenshots in image viewer so I can actually see what's on them"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ No screenshots directory found")
        return

    # Get the most recent screenshots
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    recent_files = [f for f in all_files if '_211' in f]  # Today's screenshots
    recent_files.sort()

    if not recent_files:
        print("❌ No recent screenshots found")
        return

    print(f"🖼️  Opening {len(recent_files)} recent screenshots for LLM inspection...")
    print("As an LLM, I need to actually SEE these images to understand what's happening")
    print("Each screenshot will open in your default image viewer")
    print()

    for i, filename in enumerate(recent_files[:5], 1):  # Open first 5
        filepath = os.path.join(screenshots_dir, filename)
        print(f"📸 Opening screenshot {i}: {filename}")

        try:
            # Open with default Windows image viewer
            subprocess.run(["start", filepath], shell=True, check=True)
            time.sleep(2)  # Give time to view each one
        except Exception as e:
            print(f"❌ Could not open {filename}: {e}")

        if i < 5:
            input("Press Enter to continue to next screenshot...")

    print("\n✅ All screenshots opened for inspection!")
    print("Now I can SEE what's actually happening in the automated test...")

def inspect_specific_screenshot(filename):
    """Open a specific screenshot for detailed inspection"""

    filepath = os.path.join("test_screenshots", filename)
    if not os.path.exists(filepath):
        print(f"❌ {filename} not found")
        return

    print(f"🔍 Inspecting: {filename}")
    try:
        subprocess.run(["start", filepath], shell=True, check=True)
        print("✅ Opened for inspection")
    except Exception as e:
        print(f"❌ Could not open: {e}")

if __name__ == "__main__":
    print("🤖 LLM SCREENSHOT INSPECTION")
    print("=" * 50)
    print("As an LLM, I need to actually LOOK at these PNG files")
    print("to understand if the automated test is working...")
    print()

    # Open key screenshots for inspection
    key_screenshots = [
        "01_initial_page_211558.png",
        "02_after_start_211600.png",
        "03_motion_1_start_211600.png",
        "05_results_page_211614.png"
    ]

    for screenshot in key_screenshots:
        inspect_specific_screenshot(screenshot)
        input(f"Look at {screenshot} and press Enter when ready...")

    print("\n🎯 LLM ANALYSIS COMPLETE")
    print("Now I can tell you what I SEE in these screenshots...")