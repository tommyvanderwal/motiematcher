#!/usr/bin/env python3
"""
Activate browser window for testing
"""

import pyautogui
import time

def activate_browser():
    """Try to activate the browser window"""

    print("🔍 Activating browser window...")

    # Method 1: Alt+Tab to cycle to browser
    print("🔄 Using Alt+Tab to find browser...")
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1)

    # Take screenshot to check current screen
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size

    # Analyze screen content
    light_pixels = 0
    text_like_pixels = 0

    for x in range(100, width-100, 50):
        for y in range(100, height-100, 50):
            pixel = screenshot.getpixel((x, y))
            if sum(pixel) > 600:  # Very light (white background)
                light_pixels += 1
            # Check for text-like contrast
            neighbors = []
            for dx in [-5, 0, 5]:
                for dy in [-5, 0, 5]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors.append(screenshot.getpixel((nx, ny)))

            if neighbors:
                avg_neighbor = sum(sum(n) for n in neighbors) / len(neighbors) / 3
                if abs(sum(pixel) - avg_neighbor) > 100:  # High contrast
                    text_like_pixels += 1

    total_samples = ((width-200)//50 + 1) * ((height-200)//50 + 1)
    light_ratio = light_pixels / total_samples
    text_ratio = text_like_pixels / total_samples

    print(f"📊 Screen analysis: {light_ratio:.2f} light, {text_ratio:.2f} text-like")

    if light_ratio > 0.3 and text_ratio > 0.1:
        print("✅ Browser appears to be active with web content")
        return True
    else:
        print("❌ Browser not found or not displaying web content")
        print("💡 Try manually opening http://localhost:51043 in your browser")
        return False

if __name__ == "__main__":
    success = activate_browser()
    if success:
        print("🎯 Browser is ready for testing!")
    else:
        print("❌ Could not activate browser")