#!/usr/bin/env python3
"""
Improved smart automated test with better color detection
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Sequence, Tuple, cast

import pyautogui

BASE_URL = os.environ.get("MOTIEMATCHER_BASE_URL", "http://127.0.0.1:8001")

def _ensure_rgb(color) -> Tuple[int, int, int]:
    """Convert raw pixel values to an RGB tuple."""
    if isinstance(color, Sequence):
        components = [int(component) for component in color[:3]]
        while len(components) < 3:
            components.append(components[-1] if components else 0)
        return cast(Tuple[int, int, int], tuple(components[:3]))

    value = int(color) if color is not None else 0
    return cast(Tuple[int, int, int], (value, value, value))


def find_button_in_content_area(button_type):
    """Find button by looking in content areas with text"""

    print(f"[SCAN] Looking for {button_type} button in content areas...")

    screenshot = pyautogui.screenshot()
    width, height = screenshot.size

    if screenshot.mode != 'RGB':
        screenshot = screenshot.convert('RGB')

    # Find areas with text (high contrast)
    text_regions = []

    for x in range(200, width-200, 100):
        for y in range(200, height-200, 100):
            center = _ensure_rgb(screenshot.getpixel((x, y)))
            center_brightness = sum(center) / 3

            # Check contrast with neighbors
            contrasts = []
            for dx in [-20, 0, 20]:
                for dy in [-20, 0, 20]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor = _ensure_rgb(screenshot.getpixel((nx, ny)))
                        neighbor_brightness = sum(neighbor) / 3
                        contrasts.append(abs(center_brightness - neighbor_brightness))

            if contrasts:
                avg_contrast = sum(contrasts) / len(contrasts)
                if avg_contrast > 30:  # Text-like contrast
                    text_regions.append((x, y))

    print(f"[INFO] Found {len(text_regions)} text regions")

    # In text regions, look for button colors
    button_colors = {
        'start': [(0, 123, 255), (13, 110, 253), (0, 86, 179)],  # Blue variations
        'voor': [(25, 135, 84), (40, 167, 69), (0, 100, 0)],     # Green variations
        'tegen': [(220, 53, 69), (201, 25, 11), (150, 0, 0)],    # Red variations
        'results': [(0, 123, 255), (13, 110, 253)]               # Blue
    }

    target_colors = button_colors.get(button_type, [])
    if not target_colors:
        print(f"[ERROR] Unknown button type: {button_type}")
        return None

    best_match = None
    best_distance = float('inf')

    # Search in text regions and nearby areas
    for text_x, text_y in text_regions[:50]:  # Check first 50 text regions
        # Search in a 200x200 area around each text region
        search_size = 200
        for x in range(max(0, text_x - search_size//2), min(width, text_x + search_size//2), 20):
            for y in range(max(0, text_y - search_size//2), min(height, text_y + search_size//2), 20):
                pixel = _ensure_rgb(screenshot.getpixel((x, y)))

                # Check distance to target colors
                for target_color in target_colors:
                    target_color = _ensure_rgb(target_color)
                    dr = pixel[0] - target_color[0]
                    dg = pixel[1] - target_color[1]
                    db = pixel[2] - target_color[2]
                    distance = (dr * dr + dg * dg + db * db) ** 0.5
                    if distance < best_distance and distance < 60:  # Within tolerance
                        best_distance = distance
                        best_match = (x, y, pixel, target_color)

    if best_match:
        x, y, found_color, target_color = best_match
        print(f"[SUCCESS] Found {button_type} button at ({x}, {y})")
        print(f"          Found color: RGB{found_color}, Target: RGB{target_color}, Distance: {best_distance:.1f}")
        return (x, y)
    else:
        print(f"[WARN] {button_type} button not found in text regions")
        return None

def smart_click_improved(button_type):
    """Improved smart click using content area detection"""

    position = find_button_in_content_area(button_type)
    if position:
        x, y = position
        print(f"[ACTION] Clicking {button_type} at ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(2)  # Longer wait for page load

        return True
    else:
        return False

def take_timestamped_screenshot(name):
    """Take screenshot with timestamp"""

    timestamp = time.strftime("%H%M%S")
    filename = f"test_screenshots/{name}_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"[SNAPSHOT] Saved: {filename}")
    return filename

def get_motion_count(default: int = 5) -> int:
    """Fetch the number of motions exposed by the API."""
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/motions", timeout=5) as response:
            data = json.load(response)
            motions = data.get("motions", [])
            if isinstance(motions, list) and motions:
                return len(motions)
    except Exception as err:
        print(f"[WARN] Could not determine motion count via API: {err}")
    return default


def run_improved_smart_test():
    """Run improved smart automated test"""

    print("[START] Improved smart automated test")
    print("=" * 50)
    print("Using content-aware button detection")

    os.makedirs("test_screenshots", exist_ok=True)

    # Initial screenshot
    take_timestamped_screenshot("01_initial_page")

    # Click start button
    if not smart_click_improved('start'):
        print("[WARN] Could not find start button - checking if already on motion page...")

        # Maybe we're already on a motion page, try clicking 'voor'
        if not smart_click_improved('voor'):
            print("[ERROR] Test failed - no recognizable buttons found")
            return False

    take_timestamped_screenshot("02_after_start")

    # Vote on motions
    total_motions = get_motion_count()
    print(f"[INFO] Using total motions: {total_motions}")

    for i in range(1, total_motions + 1):
        take_timestamped_screenshot(f"03_motion_{i}_start")

        vote = 'voor' if i % 2 == 1 else 'tegen'
        if not smart_click_improved(vote):
            print(f"[WARN] Could not find {vote} button for motion {i}, trying other vote...")
            other_vote = 'tegen' if vote == 'voor' else 'voor'
            if not smart_click_improved(other_vote):
                print(f"[ERROR] Could not vote on motion {i}")
                return False

        take_timestamped_screenshot(f"04_motion_{i}_voted_{vote}")

    # Go to results
    if not smart_click_improved('results'):
        print("[WARN] Could not find results button - assuming results page is already visible")
    else:
        time.sleep(2)

    take_timestamped_screenshot("05_results_page")

    # Scroll
    pyautogui.scroll(-500)
    time.sleep(1)
    take_timestamped_screenshot("06_results_scrolled")

    print("\n[COMPLETE] Improved smart test finished successfully")
    return True

if __name__ == "__main__":
    success = run_improved_smart_test()

    if success:
        if os.environ.get("RUN_LLM_ANALYSIS") == "1":
            print("\n[INFO] Analyzing results...")
            subprocess.run([sys.executable, "llm_direct_analysis.py"], check=False)
        else:
            print("\n[INFO] Skipping LLM analysis (set RUN_LLM_ANALYSIS=1 to enable)")
    else:
        print("\n[ERROR] Test failed")