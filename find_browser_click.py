#!/usr/bin/env python3
"""
Find browser window position and click on correct coordinates
"""

import pyautogui
import time

def find_browser_and_click():
    """Find browser window and click on correct positions"""

    print("🔍 Finding browser window position...")

    # Get screen info
    screen_width, screen_height = pyautogui.size()
    print(f"📐 Screen: {screen_width}x{screen_height}")

    # Take screenshot to analyze
    screenshot = pyautogui.screenshot()

    # Find browser window boundaries by looking for content area
    # Assume browser window starts after dark borders/title bar

    # Look for the main content area (usually light)
    content_start_y = 0
    content_start_x = 0

    # Scan from top to find where content begins (skip title bar)
    for y in range(50, screen_height // 2, 10):
        light_pixels = 0
        for x in range(100, screen_width - 100, 50):
            pixel = screenshot.getpixel((x, y))
            if sum(pixel) > 400:  # Light pixel
                light_pixels += 1

        if light_pixels > 10:  # Found content area
            content_start_y = y
            break

    # Scan from left to find content start
    for x in range(50, screen_width // 2, 10):
        light_pixels = 0
        for y in range(content_start_y, content_start_y + 200, 20):
            if y < screenshot.height:
                pixel = screenshot.getpixel((x, y))
                if sum(pixel) > 400:
                    light_pixels += 1

        if light_pixels > 5:
            content_start_x = x
            break

    print(f"📍 Content area starts at: ({content_start_x}, {content_start_y})")

    # Calculate button positions relative to content area
    content_width = screen_width - 2 * content_start_x
    content_height = screen_height - content_start_y - 100  # Leave room for bottom

    print(f"📐 Content area: {content_width}x{content_height}")

    # Button positions (estimated)
    start_button_x = content_start_x + content_width // 2
    start_button_y = content_start_y + content_height // 2

    vote_button_left_x = content_start_x + content_width // 2 - 150
    vote_button_right_x = content_start_x + content_width // 2 + 150
    vote_button_y = content_start_y + content_height // 2 + 150

    results_button_x = content_start_x + content_width // 2
    results_button_y = content_start_y + content_height - 100

    print("🎯 Calculated button positions:")
    print(f"   Start button: ({start_button_x}, {start_button_y})")
    print(f"   Voor button: ({vote_button_left_x}, {vote_button_y})")
    print(f"   Tegen button: ({vote_button_right_x}, {vote_button_y})")
    print(f"   Results button: ({results_button_x}, {results_button_y})")

    # Test clicking on start button
    print("\n🖱️  Testing start button click...")
    pyautogui.moveTo(start_button_x, start_button_y, duration=1)
    time.sleep(0.5)

    # Check pixel at cursor
    test_screenshot = pyautogui.screenshot()
    if (0 <= start_button_x < test_screenshot.width and
        0 <= start_button_y < test_screenshot.height):
        pixel_at_cursor = test_screenshot.getpixel((start_button_x, start_button_y))
        print(f"🎨 Pixel at cursor: {pixel_at_cursor}")

    pyautogui.click()
    print("✅ Clicked start button")

    # Wait and take screenshot
    time.sleep(2)
    after_click = pyautogui.screenshot()
    after_click.save("test_screenshots/test_click_result.png")
    print("📸 Screenshot saved: test_screenshots/test_click_result.png")

    return {
        'content_start': (content_start_x, content_start_y),
        'start_button': (start_button_x, start_button_y),
        'vote_buttons': (vote_button_left_x, vote_button_right_x, vote_button_y),
        'results_button': (results_button_x, results_button_y)
    }

if __name__ == "__main__":
    positions = find_browser_and_click()
    print(f"\n📍 Found positions: {positions}")