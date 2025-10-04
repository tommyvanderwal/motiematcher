#!/usr/bin/env python3
"""
Simple test - just check if web app loads
"""

import time
import pyautogui
import os

def simple_test():
    """Simple test to check if web app loads"""

    print("🧪 SIMPLE WEB APP TEST")
    print("This will:")
    print("1. Wait 3 seconds for browser to load")
    print("2. Take a screenshot")
    print("3. Analyze what we see")

    time.sleep(3)  # Wait for browser

    # Take screenshot
    screenshot = pyautogui.screenshot()

    # Save it
    os.makedirs("test_screenshots", exist_ok=True)
    screenshot_path = "test_screenshots/manual_check.png"
    screenshot.save(screenshot_path)

    print(f"📸 Screenshot saved: {screenshot_path}")

    # Analyze
    width, height = screenshot.size
    print(f"📐 Screenshot size: {width}x{height}")

    # Check center pixel
    center_pixel = screenshot.getpixel((width//2, height//2))
    print(f"🎯 Center pixel: {center_pixel}")

    # Check average brightness
    if screenshot.mode != 'RGB':
        screenshot = screenshot.convert('RGB')

    pixels = []
    sample_size = 50
    for x in range(max(0, width//2 - sample_size), min(width, width//2 + sample_size)):
        for y in range(max(0, height//2 - sample_size), min(height, height//2 + sample_size)):
            pixels.append(screenshot.getpixel((x, y)))

    if pixels:
        avg_brightness = sum(sum(p) for p in pixels) / len(pixels) / 3 / 255
        print(f"💡 Average brightness: {avg_brightness:.3f}")

        if avg_brightness > 0.9:
            print("⚠️  EXTREMELY BRIGHT - Probably empty/white screen!")
        elif avg_brightness > 0.6:
            print("✅ Light background (typical web page)")
        else:
            print("🤔 Dark or medium background")

    print("\n❓ QUESTION: Do you see the MotieMatcher web app in your browser?")
    print("If not, the automated test is definitely broken!")

if __name__ == "__main__":
    simple_test()