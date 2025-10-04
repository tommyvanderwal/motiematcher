#!/usr/bin/env python3
"""
Check current screen status
"""

import pyautogui

def check_screen():
    """Check what the current screen looks like"""

    print("🔍 Checking current screen status...")

    # Get screen info
    screen_size = pyautogui.size()
    mouse_pos = pyautogui.position()

    print(f"📐 Screen size: {screen_size}")
    print(f"🖱️  Mouse position: {mouse_pos}")

    # Take screenshot
    screenshot = pyautogui.screenshot()
    print(f"📸 Screenshot size: {screenshot.size}")
    print(f"🎨 Screenshot mode: {screenshot.mode}")

    # Check center pixel
    center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
    center_pixel = screenshot.getpixel((center_x, center_y))
    print(f"🎯 Center pixel color: {center_pixel}")

    # Check average brightness
    if screenshot.mode != 'RGB':
        screenshot = screenshot.convert('RGB')

    pixels = []
    sample_size = 50
    for x in range(max(0, center_x - sample_size), min(screen_size[0], center_x + sample_size)):
        for y in range(max(0, center_y - sample_size), min(screen_size[1], center_y + sample_size)):
            pixels.append(screenshot.getpixel((x, y)))

    if pixels:
        avg_brightness = sum(sum(p) for p in pixels) / len(pixels) / 3 / 255
        print(f"💡 Average brightness: {avg_brightness:.3f}")

        if avg_brightness > 0.9:
            print("⚠️  EXTREMELY BRIGHT - Screen appears to be mostly white/empty!")
        elif avg_brightness > 0.6:
            print("✅ Light background (typical web page)")
        elif avg_brightness < 0.3:
            print("⚠️  Dark background")
        else:
            print("🤔 Medium brightness")

    return {
        'screen_size': screen_size,
        'mouse_pos': mouse_pos,
        'center_pixel': center_pixel,
        'avg_brightness': avg_brightness if pixels else None
    }

if __name__ == "__main__":
    check_screen()