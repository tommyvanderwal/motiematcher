#!/usr/bin/env python3
"""
Improved Automated Test with Correct Browser Detection
"""

import pyautogui
import time
import os
from PIL import Image

def find_browser_window():
    """Find browser window position and content area"""

    print("🔍 Finding browser window...")

    screenshot = pyautogui.screenshot()
    screen_width, screen_height = screenshot.size

    # Find content area (skip title bar and borders)
    content_start_y = 120  # Based on previous analysis
    content_start_x = 0

    # Verify content area has actual content
    light_pixels = 0
    for x in range(200, screen_width - 200, 50):
        for y in range(content_start_y, content_start_y + 300, 30):
            pixel = screenshot.getpixel((x, y))
            if sum(pixel) > 500:  # Light pixel
                light_pixels += 1

    if light_pixels < 20:
        print("⚠️  Warning: Low light pixels detected - browser might not be visible")
        return None

    print(f"✅ Found content area at ({content_start_x}, {content_start_y})")

    # Calculate button positions
    start_button_x = screen_width // 2
    start_button_y = content_start_y + (screen_height - content_start_y) // 2

    vote_button_left_x = screen_width // 2 - 150
    vote_button_right_x = screen_width // 2 + 150
    vote_button_y = start_button_y + 150

    results_button_x = screen_width // 2
    results_button_y = screen_height - 200

    positions = {
        'start': (start_button_x, start_button_y),
        'voor': (vote_button_left_x, vote_button_y),
        'tegen': (vote_button_right_x, vote_button_y),
        'results': (results_button_x, results_button_y)
    }

    print("🎯 Button positions:")
    for name, (x, y) in positions.items():
        print(f"   {name}: ({x}, {y})")

    return positions

def take_screenshot(name):
    """Take screenshot with timestamp"""
    timestamp = time.strftime("%H%M%S")
    filename = f"test_screenshots/{name}_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"📸 Saved: {filename}")
    return filename

def click_button(position, name):
    """Click button at position"""
    x, y = position
    print(f"🖱️  Clicking {name} at ({x}, {y})")

    pyautogui.moveTo(x, y, duration=0.5)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(1)  # Wait for page to load

def run_improved_test():
    """Run the improved automated test"""

    print("🚀 STARTING IMPROVED AUTOMATED TEST")
    print("=" * 50)

    # Ensure screenshots directory exists
    os.makedirs("test_screenshots", exist_ok=True)

    # Step 1: Find browser window
    positions = find_browser_window()
    if not positions:
        print("❌ Could not find browser window")
        return False

    # Step 2: Take initial screenshot
    take_screenshot("01_initial_page")

    # Step 3: Click start button
    click_button(positions['start'], "START button")
    take_screenshot("02_after_start")

    # Step 4: Vote on 5 motions
    for i in range(1, 6):
        take_screenshot(f"03_motion_{i}_start")

        # Alternate votes: voor, tegen, voor, tegen, voor
        vote = "voor" if i % 2 == 1 else "tegen"
        click_button(positions[vote], f"{vote.upper()} button")
        take_screenshot(f"04_motion_{i}_voted_{vote}")

    # Step 5: Go to results
    click_button(positions['results'], "RESULTS button")
    take_screenshot("05_results_page")

    # Step 6: Scroll down to see more results
    pyautogui.scroll(-500)  # Scroll down
    time.sleep(1)
    take_screenshot("06_results_scrolled")

    print("\n🎉 TEST COMPLETED!")
    print("📊 Check test_screenshots/ for results")

    return True

if __name__ == "__main__":
    success = run_improved_test()
    if success:
        print("\n🔍 Analyzing results...")
        # Run analysis
        os.system("py analyze_screenshot_content.py")
    else:
        print("❌ Test failed")