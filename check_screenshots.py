#!/usr/bin/env python3
"""
Screenshot Analysis Script - Check what actually happened in the test
"""

import os
from PIL import Image
import datetime

def analyze_recent_screenshots():
    """Analyze the most recent test screenshots to see what actually happened"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ Screenshots directory not found")
        return

    # Get most recent screenshots (2036xx timestamps)
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    recent_files = [f for f in all_files if '_2036' in f or '_2035' in f]
    recent_files.sort()

    print("🔍 Analyzing Most Recent Screenshots")
    print(f"Found {len(recent_files)} recent screenshots")
    print("=" * 60)

    for filename in recent_files:
        filepath = os.path.join(screenshots_dir, filename)

        try:
            img = Image.open(filepath)
            width, height = img.size
            file_size = os.path.getsize(filepath)

            print(f"\n📸 {filename}")
            print(f"   Size: {width}x{height} pixels")
            print(f"   File size: {file_size} bytes")

            # Analyze based on filename
            if "01_initial_page" in filename:
                print("   🎯 Should show: Start page with 'Start Stemming' button")
                print("   ❓ Does it show the web app or something else?")

            elif "02_after_start" in filename:
                print("   🚀 Should show: First motion after clicking start")
                print("   ❓ Did the click work? Is there a motion visible?")

            elif filename.startswith("03_motion_"):
                motion_num = filename.split('_')[2]
                print(f"   📄 Should show: Motion {motion_num} display")
                print("   ❓ Is motion text visible? Are vote buttons there?")

            elif filename.startswith("04_motion_"):
                parts = filename.split('_')
                motion_num = parts[2]
                vote = parts[4]
                print(f"   🗳️  Should show: Motion {motion_num} after voting '{vote}'")
                print("   ❓ Did the vote register? Any confirmation?")

            elif "05_results_page" in filename:
                print("   📊 Should show: Results summary")
                print("   ❓ Are results displayed? Any data visible?")

            elif "06_results_scrolled" in filename:
                print("   📜 Should show: Scrolled results")
                print("   ❓ More details visible after scrolling?")

            # Try to open the image for manual inspection
            print(f"   👀 Opening image for inspection...")
            img.show()

            # Wait for user to close the image
            input("   Press Enter after viewing the image...")

        except Exception as e:
            print(f"   ❌ Error opening {filename}: {e}")

    print("\n" + "=" * 60)
    print("🎯 ANALYSIS COMPLETE")
    print("Based on what you saw in the images, does the test actually work?")
    print("Are the clicks hitting the right buttons?")
    print("Is the web app actually loading and responding?")

if __name__ == "__main__":
    analyze_recent_screenshots()