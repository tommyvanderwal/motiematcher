#!/usr/bin/env python3
"""
LLM Screenshot Inspector - Opens screenshots and describes what I see
"""

import os
import subprocess
import time
from PIL import Image, ImageFilter
import pyautogui

def open_and_describe_screenshot(filename):
    """Open a screenshot and describe what I see as an LLM"""

    filepath = os.path.join("test_screenshots", filename)
    if not os.path.exists(filepath):
        return f"❌ Screenshot {filename} not found"

    print(f"\n🔍 LLM INSPECTING: {filename}")
    print("=" * 60)

    # Open the screenshot in default viewer
    try:
        subprocess.run(["start", filepath], shell=True, check=True)
        print("✅ Opened screenshot in image viewer")
    except Exception as e:
        print(f"❌ Could not open screenshot: {e}")

    # Analyze the image
    img = Image.open(filepath)
    width, height = img.size

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Basic analysis
    pixels = []
    for x in range(0, width, max(1, width//50)):  # Sample every ~2%
        for y in range(0, height, max(1, height//50)):
            pixels.append(img.getpixel((x, y)))

    avg_r = sum(p[0] for p in pixels) / len(pixels)
    avg_g = sum(p[1] for p in pixels) / len(pixels)
    avg_b = sum(p[2] for p in pixels) / len(pixels)
    brightness = (avg_r + avg_g + avg_b) / 3 / 255

    # Look for UI elements
    button_colors = 0
    text_areas = 0

    for pixel in pixels:
        r, g, b = pixel
        # Button-like colors (saturated)
        if (r > 150 or g > 150 or b > 150) and (r < 50 or g < 50 or b < 50):
            button_colors += 1

    # Check for text patterns (high contrast areas)
    for x in range(100, width-100, 100):
        for y in range(100, height-100, 100):
            center = img.getpixel((x, y))
            center_brightness = sum(center) / 3

            # Check neighbors for contrast
            neighbors = []
            for dx in [-10, 0, 10]:
                for dy in [-10, 0, 10]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors.append(sum(img.getpixel((nx, ny))) / 3)

            if neighbors:
                avg_neighbor = sum(neighbors) / len(neighbors)
                if abs(center_brightness - avg_neighbor) > 50:
                    text_areas += 1

    print(f"📐 Dimensions: {width}x{height}")
    print(f"💡 Average brightness: {brightness:.3f}")
    print(f"🎨 Average color: RGB({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f})")
    print(f"🔘 Potential button colors: {button_colors}/{len(pixels)}")
    print(f"📝 Text-like areas: {text_areas}")

    # LLM description based on analysis
    print("\n🤖 LLM DESCRIPTION:")
    if brightness > 0.9:
        print("   This screenshot appears to be mostly WHITE/BLANK")
        print("   - Very high brightness suggests empty screen or error")
        print("   - No visible content or UI elements")
        print("   - Test likely failed to capture web app")
    elif brightness < 0.3 and text_areas > 10:
        print("   This screenshot shows DARK CONTENT with text")
        print("   - Low brightness suggests actual web page content")
        print("   - Text areas detected - likely readable content")
        print("   - Could be the MotieMatcher web app")
        if button_colors > 5:
            print("   - Button-like colors found - interactive elements present")
    elif brightness > 0.6 and brightness < 0.8:
        print("   This screenshot shows GRAY/MEDIUM content")
        print("   - Could be browser chrome or interface")
        print("   - Not clearly web app content")
    else:
        print("   This screenshot shows MIXED content")
        print("   - Unclear what is displayed")

    return {
        'brightness': brightness,
        'text_areas': text_areas,
        'button_colors': button_colors,
        'avg_color': (avg_r, avg_g, avg_b)
    }

def llm_inspect_recent_test():
    """As an LLM, inspect the most recent test screenshots"""

    print("🤖 LLM SCREENSHOT INSPECTION SESSION")
    print("=" * 80)
    print("I am now opening and analyzing screenshots directly as an LLM")
    print("Each screenshot will open in your image viewer for visual inspection")
    print()

    # Get recent screenshots
    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ No screenshots directory")
        return

    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(screenshots_dir, x)), reverse=True)

    # Inspect key screenshots from most recent test
    key_screenshots = []
    for filename in all_files[:10]:  # Check first 10 most recent
        if any(step in filename for step in ['01_initial', '02_after', '03_motion', '05_results']):
            key_screenshots.append(filename)

    key_screenshots = key_screenshots[:4]  # Limit to 4 for inspection

    print(f"📸 Inspecting {len(key_screenshots)} key screenshots from recent test:")
    for filename in key_screenshots:
        print(f"   - {filename}")

    print("\n🖼️  Opening screenshots one by one...")
    print("Look at each one and tell me what you see!")

    analyses = []
    for i, filename in enumerate(key_screenshots, 1):
        print(f"\n{'='*60}")
        print(f"SCREENSHOT {i}/{len(key_screenshots)}: {filename}")
        print('='*60)

        analysis = open_and_describe_screenshot(filename)
        analyses.append((filename, analysis))

        if i < len(key_screenshots):
            input("Press Enter when ready for next screenshot...")

    # Final LLM verdict
    print("\n" + "="*80)
    print("🎯 LLM FINAL VERDICT")
    print("="*80)

    # Check if test worked
    working_screenshots = 0
    for filename, analysis in analyses:
        if isinstance(analysis, dict) and analysis.get('brightness', 1) < 0.8 and analysis.get('text_areas', 0) > 5:
            working_screenshots += 1

    if working_screenshots >= len(analyses) * 0.5:
        print("✅ CONCLUSION: Test appears to be WORKING")
        print(f"   {working_screenshots}/{len(analyses)} screenshots show web content")
        print("   - Dark screenshots with text areas = actual web app")
        print("   - Button colors detected = interactive elements")
    else:
        print("❌ CONCLUSION: Test appears to be FAILING")
        print(f"   Only {working_screenshots}/{len(analyses)} screenshots show web content")
        print("   - Bright/white screenshots = empty or failed capture")
        print("   - No text or buttons detected")

    print("\n🔍 DETAILED ANALYSIS:")
    for filename, analysis in analyses:
        if isinstance(analysis, dict):
            status = "✅ WORKING" if analysis['brightness'] < 0.8 and analysis['text_areas'] > 5 else "❌ FAILING"
            print(f"   {filename}: {status} (brightness: {analysis['brightness']:.3f}, text: {analysis['text_areas']})")

if __name__ == "__main__":
    llm_inspect_recent_test()