#!/usr/bin/env python3
"""
Simple screenshot analysis - no user input, no emoji
"""

from PIL import Image
import os

def analyze_latest_screenshot():
    """Analyze the most recent screenshot"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("No screenshots directory")
        return

    # Get most recent screenshot
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    if not all_files:
        print("No screenshots found")
        return

    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(screenshots_dir, x)), reverse=True)
    latest_file = all_files[0]
    filepath = os.path.join(screenshots_dir, latest_file)

    print(f"Analyzing latest screenshot: {latest_file}")

    try:
        img = Image.open(filepath)
        width, height = img.size

        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Sample pixels
        samples = []
        for x in range(0, width, 100):
            for y in range(0, height, 100):
                samples.append(img.getpixel((x, y)))

        if samples:
            avg_brightness = sum(sum(p) for p in samples) / len(samples) / 3 / 255
            non_white = sum(1 for p in samples if p != (255, 255, 255))
            dark_pixels = sum(1 for p in samples if sum(p) < 150)

            print(f"Size: {width}x{height}")
            print(f"Brightness: {avg_brightness:.3f}")
            print(f"Non-white pixels: {non_white}/{len(samples)}")
            print(f"Dark pixels: {dark_pixels}/{len(samples)}")

            if avg_brightness > 0.9:
                print("STATUS: Mostly white/empty")
            elif dark_pixels > len(samples) * 0.5:
                print("STATUS: Contains dark content (likely web page)")
            else:
                print("STATUS: Mixed content")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_latest_screenshot()