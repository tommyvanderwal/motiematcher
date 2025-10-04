#!/usr/bin/env python3
"""
Debug script to take screenshot and analyze screen content
"""

import pyautogui
from PIL import Image
import time

def main():
    print("Taking debug screenshot...")
    time.sleep(2)  # Wait a bit

    screenshot = pyautogui.screenshot()
    screenshot.save('debug_current_screen.png')
    print("Screenshot saved as debug_current_screen.png")

    # Get screen size
    width, height = screenshot.size
    print(f"Screen size: {width}x{height}")

    # Check if screenshot has content (not just empty)
    # Sample some pixels to see if there's variation
    pixels = []
    for x in [100, 300, 500, 700]:
        for y in [100, 300, 500, 700]:
            if x < width and y < height:
                pixel = screenshot.getpixel((x, y))
                pixels.append(pixel)

    print(f"Sample pixels: {pixels[:5]}...")

    # Check for blue colors (Bootstrap buttons are often blue)
    blue_pixels = 0
    for pixel in pixels:
        r, g, b = pixel
        if b > r and b > g and b > 100:  # Blue dominant
            blue_pixels += 1

    print(f"Blue pixels in sample: {blue_pixels}/{len(pixels)}")

if __name__ == "__main__":
    main()