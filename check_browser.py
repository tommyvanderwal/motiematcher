#!/usr/bin/env python3
"""
Check if browser window is visible and find its position
"""

import pyautogui
import time

def check_browser_window():
    """Check if browser window is visible and find its position"""

    print("🔍 Checking for browser window...")

    # Wait a bit for browser to load
    time.sleep(2)

    # Try to find browser window by looking for common browser elements
    screen_width, screen_height = pyautogui.size()

    # Take screenshot and analyze
    screenshot = pyautogui.screenshot()

    # Look for browser-like patterns
    # Browsers typically have:
    # - URL bar at top
    # - Content area below
    # - Often white/light background

    # Check top area (where URL bar would be)
    top_pixels = []
    for x in range(100, screen_width - 100, 50):
        for y in range(50, 150, 10):
            if 0 <= x < screenshot.width and 0 <= y < screenshot.height:
                top_pixels.append(screenshot.getpixel((x, y)))

    if top_pixels:
        # Calculate average color of top area
        avg_r = sum(p[0] for p in top_pixels) / len(top_pixels)
        avg_g = sum(p[1] for p in top_pixels) / len(top_pixels)
        avg_b = sum(p[2] for p in top_pixels) / len(top_pixels)

        print(f"🎨 Top area average color: ({avg_r:.1f}, {avg_g:.1f}, {avg_b:.1f})")

        # Light colors suggest browser chrome
        if avg_r > 200 and avg_g > 200 and avg_b > 200:
            print("✅ Light top area - likely browser chrome")
        else:
            print("⚠️  Dark top area - might not be browser")

    # Check if we can find text-like patterns
    # Look for high contrast areas (text)
    contrast_areas = 0
    for x in range(200, screen_width - 200, 100):
        for y in range(200, screen_height - 200, 100):
            if 0 <= x < screenshot.width and 0 <= y < screenshot.height:
                pixel = screenshot.getpixel((x, y))
                # Check neighboring pixels for contrast
                neighbors = []
                for dx in [-5, 0, 5]:
                    for dy in [-5, 0, 5]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < screenshot.width and 0 <= ny < screenshot.height:
                            neighbors.append(screenshot.getpixel((nx, ny)))

                if neighbors:
                    max_diff = max(max(abs(pixel[i] - n[i]) for i in range(3)) for n in neighbors)
                    if max_diff > 50:  # High contrast = likely text
                        contrast_areas += 1

    print(f"📝 High contrast areas found: {contrast_areas}")

    if contrast_areas > 10:
        print("✅ Found text-like content - browser likely loaded")
    else:
        print("⚠️  Few contrast areas - might be empty page")

    # Try to find window boundaries
    print("\n🔍 Looking for window boundaries...")

    # Look for dark borders (window edges)
    left_border_dark = 0
    for y in range(100, screen_height - 100, 50):
        pixel = screenshot.getpixel((50, y))
        if sum(pixel) < 100:  # Dark pixel
            left_border_dark += 1

    print(f"⬅️  Dark pixels on left edge: {left_border_dark}")

    if left_border_dark > 5:
        print("✅ Found window left border - browser window detected")
        return True
    else:
        print("⚠️  No clear window border - browser might be maximized or not visible")
        return False

if __name__ == "__main__":
    browser_found = check_browser_window()

    if browser_found:
        print("\n🎯 Browser window appears to be visible!")
        print("The issue might be with button positioning within the browser.")
    else:
        print("\n❌ Browser window not clearly detected.")
        print("The web app might not be loading properly.")