#!/usr/bin/env python3
"""
Analyze the most recent screenshots from the improved test
"""

from PIL import Image
import os

def analyze_recent_screenshots():
    """Analyze the most recent screenshots"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ No screenshots directory")
        return

    # Get all screenshots and sort by modification time
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(screenshots_dir, x)), reverse=True)

    print(f"📸 ANALYZING {len(all_files)} MOST RECENT SCREENSHOTS")
    print("=" * 60)

    # Analyze the 10 most recent
    for filename in all_files[:10]:
        filepath = os.path.join(screenshots_dir, filename)

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
                blue_pixels = sum(1 for p in samples if p[2] > 200 and p[0] < 100 and p[1] < 100)
                green_pixels = sum(1 for p in samples if p[1] > 150 and p[0] < 100 and p[2] < 100)
                red_pixels = sum(1 for p in samples if p[0] > 200 and p[1] < 100 and p[2] < 100)

                print(f"{filename}:")
                print(f"  Brightness: {avg_brightness:.3f}")
                print(f"  Non-white: {non_white}/{len(samples)}")
                print(f"  Dark pixels: {dark_pixels}/{len(samples)}")
                print(f"  Blue pixels: {blue_pixels}/{len(samples)}")
                print(f"  Green pixels: {green_pixels}/{len(samples)}")
                print(f"  Red pixels: {red_pixels}/{len(samples)}")

                if avg_brightness < 0.9 and (blue_pixels > 0 or green_pixels > 0 or red_pixels > 0):
                    print("  STATUS: ✅ CONTAINS WEB APP CONTENT!")
                elif avg_brightness > 0.95:
                    print("  STATUS: ❌ MOSTLY WHITE/EMPTY")
                else:
                    print("  STATUS: 🤔 MIXED CONTENT")

        except Exception as e:
            print(f"Error analyzing {filename}: {e}")

if __name__ == "__main__":
    analyze_recent_screenshots()