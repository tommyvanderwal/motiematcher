#!/usr/bin/env python3
"""
Smart automated test with color-based button detection
"""

import pyautogui
import time
import os
from PIL import Image

def find_button_by_color(target_color, color_name, tolerance=30):
    """Find button location by searching for specific color"""

    print(f"🔍 Searching for {color_name} button (RGB{target_color})...")

    # Take screenshot
    screenshot = pyautogui.screenshot()

    width, height = screenshot.size
    best_match = None
    best_distance = float('inf')

    # Search for color matches
    for x in range(100, width-100, 10):  # Skip edges
        for y in range(100, height-100, 10):
            pixel = screenshot.getpixel((x, y))
            r, g, b = pixel

            # Calculate color distance
            distance = ((r - target_color[0])**2 +
                       (g - target_color[1])**2 +
                       (b - target_color[2])**2)**0.5

            if distance < tolerance and distance < best_distance:
                best_distance = distance
                best_match = (x, y)

    if best_match:
        print(f"✅ Found {color_name} button at {best_match} (distance: {best_distance:.1f})")
        return best_match
    else:
        print(f"❌ {color_name} button not found")
        return None

def smart_click_button(button_type):
    """Smart click based on button type and color detection"""

    color_map = {
        'start': ((0, 123, 255), "blue"),      # Bootstrap btn-primary blue
        'voor': ((25, 135, 84), "green"),      # Bootstrap btn-success green
        'tegen': ((220, 53, 69), "red"),       # Bootstrap btn-danger red
        'results': ((13, 110, 253), "blue")    # Bootstrap btn-outline-primary
    }

    if button_type not in color_map:
        print(f"❌ Unknown button type: {button_type}")
        return False

    target_color, color_name = color_map[button_type]
    position = find_button_by_color(target_color, color_name)

    if position:
        x, y = position
        print(f"🖱️  Clicking {button_type} button at ({x}, {y})")

        # Move to position and click
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(1)  # Wait for page load

        return True
    else:
        print(f"❌ Could not find {button_type} button")
        return False

def take_timestamped_screenshot(name):
    """Take screenshot with timestamp"""

    timestamp = time.strftime("%H%M%S")
    filename = f"test_screenshots/{name}_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"📸 Saved: {filename}")
    return filename

def run_smart_automated_test():
    """Run automated test with smart color-based clicking"""

    print("🚀 STARTING SMART AUTOMATED TEST")
    print("=" * 50)
    print("Using color-based button detection instead of hardcoded coordinates")

    # Ensure screenshots directory exists
    os.makedirs("test_screenshots", exist_ok=True)

    # Step 1: Initial screenshot
    take_timestamped_screenshot("01_initial_page")

    # Step 2: Click start button (blue)
    if not smart_click_button('start'):
        print("❌ Could not start test - start button not found")
        return False

    take_timestamped_screenshot("02_after_start")

    # Step 3: Vote on motions
    for i in range(1, 6):
        take_timestamped_screenshot(f"03_motion_{i}_start")

        # Alternate votes
        vote_button = 'voor' if i % 2 == 1 else 'tegen'

        if not smart_click_button(vote_button):
            print(f"❌ Could not vote on motion {i}")
            return False

        take_timestamped_screenshot(f"04_motion_{i}_voted_{vote_button}")

    # Step 4: Go to results
    if not smart_click_button('results'):
        print("❌ Could not find results button")
        return False

    take_timestamped_screenshot("05_results_page")

    # Step 5: Scroll to see more
    pyautogui.scroll(-500)
    time.sleep(1)
    take_timestamped_screenshot("06_results_scrolled")

    print("\n🎉 SMART TEST COMPLETED!")
    print("📊 Check test_screenshots/ for results")

    return True

def verify_web_app_is_visible():
    """Check if web app is actually visible in browser"""

    print("🔍 Verifying web app visibility...")

    screenshot = pyautogui.screenshot()
    width, height = screenshot.size

    # Look for web page indicators
    blue_pixels = 0    # Bootstrap buttons
    green_pixels = 0   # Success buttons
    red_pixels = 0     # Danger buttons
    text_pixels = 0    # High contrast areas

    for x in range(0, width, 20):
        for y in range(0, height, 20):
            pixel = screenshot.getpixel((x, y))
            r, g, b = pixel

            # Count button colors
            if r < 50 and g > 120 and b > 200:  # Blue
                blue_pixels += 1
            if r < 50 and g > 120 and b < 100:  # Green
                green_pixels += 1
            if r > 200 and g < 80 and b < 80:   # Red
                red_pixels += 1

            # Check for text (high contrast)
            neighbors = []
            for dx in [-5, 0, 5]:
                for dy in [-5, 0, 5]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors.append(screenshot.getpixel((nx, ny)))

            if neighbors:
                avg_neighbor = sum(sum(n) for n in neighbors) / len(neighbors) / 3
                if abs(sum(pixel) / 3 - avg_neighbor) > 50:
                    text_pixels += 1

    total_samples = (width//20 + 1) * (height//20 + 1)

    print(f"   Blue pixels: {blue_pixels}/{total_samples}")
    print(f"   Green pixels: {green_pixels}/{total_samples}")
    print(f"   Red pixels: {red_pixels}/{total_samples}")
    print(f"   Text areas: {text_pixels}/{total_samples}")

    # Determine if web app is visible
    button_pixels = blue_pixels + green_pixels + red_pixels

    if button_pixels > 5 and text_pixels > 20:
        print("✅ Web app appears to be visible with buttons and text")
        return True
    else:
        print("❌ Web app not detected - browser may not be showing the page")
        return False

if __name__ == "__main__":
    # First verify web app is visible
    if not verify_web_app_is_visible():
        print("💡 Make sure the web app is running and browser is on the correct page")
        print("   Run: py -m uvicorn app.main:app --host 127.0.0.1 --port 51043")
        print("   Then open: http://localhost:51043")
        exit(1)

    # Run the smart test
    success = run_smart_automated_test()

    if success:
        print("\n🔍 Analyzing results...")
        os.system("py llm_direct_analysis.py")
    else:
        print("\n❌ Test failed")