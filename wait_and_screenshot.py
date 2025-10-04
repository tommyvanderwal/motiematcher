#!/usr/bin/env python3
"""
Wait longer and take screenshot
"""

import pyautogui
from PIL import Image
import time

def main():
    print("Waiting 10 seconds for page to load...")
    time.sleep(10)

    print("Taking screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot.save('debug_after_wait.png')
    print("Screenshot saved as debug_after_wait.png")

    # Analyze content
    width, height = screenshot.size
    print(f"Screen size: {width}x{height}")

    # Look for more color variation
    colors = set()
    for x in range(0, width, 50):
        for y in range(0, height, 50):
            pixel = screenshot.getpixel((x, y))
            colors.add(pixel)
            if len(colors) > 20:  # Limit to avoid too much output
                break
        if len(colors) > 20:
            break

    print(f"Unique colors found: {len(colors)}")
    print(f"Sample colors: {list(colors)[:10]}")

if __name__ == "__main__":
    main()