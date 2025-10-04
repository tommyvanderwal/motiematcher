#!/usr/bin/env python3
"""
Open and describe recent screenshots to see what's actually happening
"""

import os
import subprocess
from PIL import Image
import time

def open_recent_screenshots():
    """Open the most recent screenshots to see what's actually on them"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ No screenshots directory")
        return

    # Get today's screenshots (211xxx timestamps)
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    recent_files = [f for f in all_files if '_211' in f]
    recent_files.sort()

    print(f"📸 Opening {len(recent_files)} recent screenshots...")
    print("This will open each screenshot in your default image viewer")
    print("Press Enter to continue...")
    input()

    for filename in recent_files:
        filepath = os.path.join(screenshots_dir, filename)
        print(f"\n🔍 Opening: {filename}")

        # Open with default image viewer
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["start", filepath], shell=True, check=True)
            else:
                subprocess.run(["xdg-open", filepath], check=True)
        except:
            print(f"❌ Could not open {filename}")

        # Wait a bit between openings
        time.sleep(1)

    print("\n✅ All screenshots opened!")
    print("Take a look at them and tell me what you see...")

def describe_screenshot(filename):
    """Try to describe what's in a screenshot using OCR-like analysis"""

    filepath = os.path.join("test_screenshots", filename)
    if not os.path.exists(filepath):
        return f"❌ {filename} not found"

    try:
        img = Image.open(filepath)
        width, height = img.size

        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Sample pixels in a grid
        samples = []
        for x in range(100, width-100, 200):
            for y in range(100, height-100, 200):
                pixel = img.getpixel((x, y))
                samples.append(pixel)

        # Analyze colors
        avg_r = sum(p[0] for p in samples) / len(samples)
        avg_g = sum(p[1] for p in samples) / len(samples)
        avg_b = sum(p[2] for p in samples) / len(samples)

        brightness = (avg_r + avg_g + avg_b) / 3 / 255

        # Check for text-like patterns (high contrast areas)
        contrast_areas = 0
        for x in range(200, width-200, 100):
            for y in range(200, height-200, 100):
                center = img.getpixel((x, y))
                neighbors = []
                for dx in [-10, 0, 10]:
                    for dy in [-10, 0, 10]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbors.append(img.getpixel((nx, ny)))

                if neighbors:
                    avg_neighbor = sum(sum(n) for n in neighbors) / len(neighbors) / 3
                    center_brightness = sum(center) / 3
                    if abs(center_brightness - avg_neighbor) > 50:
                        contrast_areas += 1

        description = f"{filename}:\n"
        description += f"  📐 Size: {width}x{height}\n"
        description += f"  💡 Brightness: {brightness:.3f}\n"
        description += f"  🎨 Avg color: RGB({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f})\n"
        description += f"  📝 Contrast areas: {contrast_areas}\n"

        if brightness > 0.9:
            description += "  🤔 APPEARS TO BE MOSTLY WHITE/EMPTY\n"
        elif brightness < 0.3:
            description += "  ✅ CONTAINS DARK CONTENT (text/images)\n"
        else:
            description += "  🤷 MIXED CONTENT\n"

        return description

    except Exception as e:
        return f"❌ Error analyzing {filename}: {e}"

if __name__ == "__main__":
    # First describe a few key screenshots
    key_screenshots = [
        "01_initial_page_211558.png",
        "02_after_start_211600.png",
        "03_motion_1_start_211600.png",
        "05_results_page_211614.png"
    ]

    print("🔍 DESCRIBING KEY SCREENSHOTS:")
    print("=" * 50)

    for screenshot in key_screenshots:
        print(describe_screenshot(screenshot))

    print("\n🖼️  Opening screenshots in viewer...")
    open_recent_screenshots()