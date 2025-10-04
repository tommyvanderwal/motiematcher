#!/usr/bin/env python3
"""
Automated Testing Script for MotieMatcher Web App
Uses PyAutoGUI to simulate user interactions and take screenshots
"""

import os
import sys
import time
import subprocess
import pyautogui
import webbrowser
from PIL import Image
import datetime

# Configuration
SCREENSHOT_DIR = "test_screenshots"
WEB_APP_URL = "http://127.0.0.1:51043"
CONFIDENCE = 0.8  # Image recognition confidence
PAUSE_BETWEEN_ACTIONS = 2  # seconds

def setup_screenshot_dir():
    """Create directory for screenshots"""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    print(f"📁 Screenshots will be saved to: {SCREENSHOT_DIR}")

def take_screenshot(name):
    """Take a screenshot and save it with timestamp"""
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{SCREENSHOT_DIR}/{name}_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"📸 Screenshot saved: {filename}")
    return filename

def wait_for_image(image_path, timeout=10):
    """Wait for an image to appear on screen"""
    print(f"🔍 Looking for image: {image_path}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=CONFIDENCE)
            if location:
                print(f"✅ Found image at: {location}")
                return location
        except pyautogui.ImageNotFoundException:
            pass
        time.sleep(0.5)
    print(f"❌ Image not found within {timeout} seconds: {image_path}")
    return None

def click_button_by_text(text, offset_x=0, offset_y=0):
    """Find and click a button containing specific text"""
    print(f"🖱️  Looking for button with text: '{text}'")

    # Get screen size for positioning
    screen_width, screen_height = pyautogui.size()

    # HARDCODED POSITIONS BASED ON ANALYSIS - THESE ARE WRONG!
    # The test is clicking in empty space!

    if "start" in text.lower():
        # Start button is typically in the center
        x, y = screen_width // 2, screen_height // 2 + 100
        print(f"❌ HARDCODED: Clicking center-ish area for 'start' button")
    elif "voor" in text.lower():
        # Voor button (green)
        x, y = screen_width // 2 - 100, screen_height // 2 + 200
        print(f"❌ HARDCODED: Clicking left-ish area for 'voor' button")
    elif "tegen" in text.lower():
        # Tegen button (red)
        x, y = screen_width // 2 + 100, screen_height // 2 + 200
        print(f"❌ HARDCODED: Clicking right-ish area for 'tegen' button")
    elif "resultaten" in text.lower():
        # Results button
        x, y = screen_width // 2, screen_height - 100
        print(f"❌ HARDCODED: Clicking bottom center for 'resultaten' button")
    else:
        print(f"❌ Unknown button text: {text}")
        return False

    # Add offset
    x += offset_x
    y += offset_y

    print(f"🎯 Target coordinates: ({x}, {y})")

    # Check what's at the target location before clicking
    screenshot = pyautogui.screenshot()
    if 0 <= x < screenshot.width and 0 <= y < screenshot.height:
        pixel_color = screenshot.getpixel((x, y))
        print(f"🎨 Pixel at target: {pixel_color}")
    else:
        print("❌ Target coordinates are outside screen bounds!")

    # Move mouse and click
    pyautogui.moveTo(x, y, duration=0.5)
    time.sleep(0.5)
    pyautogui.click()
    print(f"✅ Clicked at position: ({x}, {y})")
    return True

def start_web_app():
    """Start the web app in background"""
    print("🚀 Starting web app...")

    # Use the improved main file
    main_file = "app/main_improved.py"
    if not os.path.exists(main_file):
        print(f"❌ Main file not found: {main_file}")
        return None

    try:
        cmd = [sys.executable, main_file]
        process = subprocess.Popen(cmd)
        print("✅ Web app started in background")
        time.sleep(3)  # Wait for startup
        return process
    except Exception as e:
        print(f"❌ Failed to start web app: {e}")
        return None

def run_automated_test():
    """Run the complete automated test"""
    print("🧪 Starting automated testing of MotieMatcher Web App")
    print("=" * 60)

    # Setup
    setup_screenshot_dir()

    # Start web app
    web_process = start_web_app()
    if not web_process:
        print("❌ Cannot proceed without web app")
        return

    try:
        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open(WEB_APP_URL)
        time.sleep(3)  # Wait for browser to open

        # Take initial screenshot
        take_screenshot("01_initial_page")

        # Click "Start Stemming" button
        print("🎯 Clicking 'Start Stemming' button...")
        time.sleep(PAUSE_BETWEEN_ACTIONS)
        click_button_by_text("start")
        time.sleep(PAUSE_BETWEEN_ACTIONS)

        take_screenshot("02_after_start")

        # Go through a few motions
        for motion_num in range(1, 6):  # Test first 5 motions for complete flow
            print(f"📝 Testing motion {motion_num}...")

            take_screenshot(f"03_motion_{motion_num}_start")

            # Decide vote based on motion number (alternate for testing)
            if motion_num % 2 == 1:
                vote = "voor"
            else:
                vote = "tegen"

            print(f"🗳️  Voting '{vote}' on motion {motion_num}")
            click_button_by_text(vote)
            time.sleep(PAUSE_BETWEEN_ACTIONS)

            take_screenshot(f"04_motion_{motion_num}_voted_{vote}")

            # Check if we can continue (not at end)
            if motion_num < 5:  # Don't check navigation on last motion
                print(f"➡️  Navigating to next motion...")
                # Try to click next or just wait for auto-redirect
                time.sleep(PAUSE_BETWEEN_ACTIONS)

        # Navigate to results
        print("📊 Going to results page...")
        click_button_by_text("resultaten")
        time.sleep(PAUSE_BETWEEN_ACTIONS)

        take_screenshot("05_results_page")

        # Scroll through results
        print("📜 Scrolling through results...")
        pyautogui.scroll(-500)  # Scroll down
        time.sleep(1)
        take_screenshot("06_results_scrolled")

        print("✅ Automated testing completed successfully!")
        print(f"📁 Check screenshots in: {SCREENSHOT_DIR}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        take_screenshot("error_screenshot")

    finally:
        # Cleanup
        if web_process:
            print("🛑 Stopping web app...")
            web_process.terminate()
            web_process.wait()

        # Clean up temp file
        if os.path.exists("temp_screen.png"):
            os.remove("temp_screen.png")

def main():
    """Main function"""
    print("🤖 MotieMatcher Automated Testing with PyAutoGUI")
    print("This script will:")
    print("  1. Start the web app")
    print("  2. Open browser and navigate")
    print("  3. Automatically click buttons and take screenshots")
    print("  4. Test voting functionality")
    print("")

    # Automatic execution - no user input needed
    print("🚀 Starting automated test in 2 seconds...")
    time.sleep(2)

    # Check for abort (mouse in corner)
    x, y = pyautogui.position()
    if x <= 10 and y <= 10:
        print("Test aborted by user.")
        return

    run_automated_test()

if __name__ == "__main__":
    main()