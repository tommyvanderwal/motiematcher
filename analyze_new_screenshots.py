#!/usr/bin/env python3
"""
Analyze the new test screenshots specifically
"""

from PIL import Image
import os

def analyze_new_screenshots():
    """Analyze screenshots from today's test run"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("No screenshots directory")
        return

    # Get today's screenshots (211xxx timestamps)
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    new_files = [f for f in all_files if '_211' in f]
    new_files.sort()

    print(f"ANALYZING {len(new_files)} NEW SCREENSHOTS")
    print("=" * 50)

    for filename in new_files:
        filepath = os.path.join(screenshots_dir, filename)

        try:
            img = Image.open(filepath)
            width, height = img.size

            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Sample pixels
            pixels = []
            for x in range(0, width, 100):
                for y in range(0, height, 100):
                    pixels.append(img.getpixel((x, y)))

            if pixels:
                avg_brightness = sum(sum(p) for p in pixels) / len(pixels) / 3 / 255
                non_white = sum(1 for p in pixels if p != (255, 255, 255))
                dark_pixels = sum(1 for p in pixels if sum(p) < 150)

                print(f"{filename}:")
                print(f"  Brightness: {avg_brightness:.3f}")
                print(f"  Non-white pixels: {non_white}/{len(pixels)}")
                print(f"  Dark pixels: {dark_pixels}/{len(pixels)}")

                if avg_brightness < 0.9 and dark_pixels > len(pixels) * 0.1:
                    print("  STATUS: Contains content!")
                else:
                    print("  STATUS: Appears empty")

        except Exception as e:
            print(f"Error analyzing {filename}: {e}")

if __name__ == "__main__":
    analyze_new_screenshots()