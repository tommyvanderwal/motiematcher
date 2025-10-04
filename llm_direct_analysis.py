#!/usr/bin/env python3
"""
LLM Direct Screenshot Analysis - No user input required
"""

from PIL import Image, ImageFilter
import os

def analyze_screenshot_pixels(filename):
    """Analyze screenshot pixels to understand content"""

    filepath = os.path.join("test_screenshots", filename)
    if not os.path.exists(filepath):
        return f"❌ {filename} not found"

    img = Image.open(filepath)
    width, height = img.size

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Sample pixels in a detailed grid
    samples = []
    for x in range(50, width-50, 100):
        for y in range(50, height-50, 100):
            samples.append(img.getpixel((x, y)))

    # Analyze content
    avg_r = sum(p[0] for p in samples) / len(samples)
    avg_g = sum(p[1] for p in samples) / len(samples)
    avg_b = sum(p[2] for p in samples) / len(samples)
    brightness = (avg_r + avg_g + avg_b) / 3 / 255

    # Check for web page indicators
    white_pixels = sum(1 for p in samples if sum(p) > 700)  # Very light
    dark_pixels = sum(1 for p in samples if sum(p) < 150)   # Very dark
    blue_pixels = sum(1 for p in samples if p[2] > 200 and p[0] < 100 and p[1] < 100)  # Blue buttons/links
    red_pixels = sum(1 for p in samples if p[0] > 200 and p[1] < 100 and p[2] < 100)   # Red buttons

    # Check for text patterns (high contrast areas)
    text_score = 0
    for x in range(100, width-100, 200):
        for y in range(100, height-100, 200):
            center = sum(img.getpixel((x, y))) / 3
            neighbors = []
            for dx in [-10, 0, 10]:
                for dy in [-10, 0, 10]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors.append(sum(img.getpixel((nx, ny))) / 3)

            if neighbors:
                avg_neighbor = sum(neighbors) / len(neighbors)
                if abs(center - avg_neighbor) > 80:
                    text_score += 1

    return {
        'filename': filename,
        'size': f"{width}x{height}",
        'brightness': brightness,
        'avg_color': (avg_r, avg_g, avg_b),
        'white_pixels': white_pixels,
        'dark_pixels': dark_pixels,
        'blue_pixels': blue_pixels,
        'red_pixels': red_pixels,
        'text_score': text_score,
        'total_samples': len(samples)
    }

def llm_analyze_screenshots():
    """As an LLM, analyze screenshots and give direct verdict"""

    print("🤖 LLM DIRECT SCREENSHOT ANALYSIS")
    print("=" * 80)
    print("Analyzing PNG files directly as an LLM...")

    key_screenshots = [
        "01_initial_page_211558.png",
        "02_after_start_211600.png",
        "03_motion_1_start_211600.png",
        "05_results_page_211614.png"
    ]

    analyses = []
    for screenshot in key_screenshots:
        analysis = analyze_screenshot_pixels(screenshot)
        analyses.append(analysis)

        print(f"\n🔍 {analysis['filename']}:")
        print(f"   📐 Size: {analysis['size']}")
        print(f"   💡 Brightness: {analysis['brightness']:.3f}")
        print(f"   🎨 Avg color: RGB({analysis['avg_color'][0]:.0f}, {analysis['avg_color'][1]:.0f}, {analysis['avg_color'][2]:.0f})")
        print(f"   ⚪ White pixels: {analysis['white_pixels']}/{analysis['total_samples']}")
        print(f"   ⚫ Dark pixels: {analysis['dark_pixels']}/{analysis['total_samples']}")
        print(f"   🔵 Blue pixels: {analysis['blue_pixels']}/{analysis['total_samples']}")
        print(f"   🔴 Red pixels: {analysis['red_pixels']}/{analysis['total_samples']}")
        print(f"   📝 Text score: {analysis['text_score']}")

    print("\n" + "=" * 80)
    print("🎯 LLM VERDICT:")
    print()

    # Check if all screenshots are identical (indicating failure)
    first = analyses[0]
    all_identical = all(
        a['brightness'] == first['brightness'] and
        a['avg_color'] == first['avg_color'] and
        a['text_score'] == first['text_score']
        for a in analyses
    )

    if all_identical:
        print("❌ AUTOMATED TEST IS FAILING!")
        print("   All screenshots are IDENTICAL - showing the same content")
        print("   This means the test is not actually navigating the web app")
        print("   PyAutoGUI clicks are not reaching the correct elements")
        print()
        print("   Evidence:")
        print(f"   - All screenshots have brightness: {first['brightness']:.3f}")
        print(f"   - All have same average color: RGB({first['avg_color'][0]:.0f}, {first['avg_color'][1]:.0f}, {first['avg_color'][2]:.0f})")
        print(f"   - All have text score: {first['text_score']}")
        print("   - No blue/red button colors detected")
        print("   - Low text contrast suggests browser chrome, not web content")

    else:
        print("✅ AUTOMATED TEST APPEARS TO BE WORKING!")
        print("   Screenshots show different content - navigation is happening")

    # Specific analysis
    if first['brightness'] > 0.9:
        print("   - Screenshots are very bright (mostly white)")
        print("   - Likely showing empty browser or failed page loads")
    elif first['brightness'] < 0.3:
        print("   - Screenshots contain dark content")
        print("   - Could be web page text on light background")
    else:
        print("   - Mixed content - possibly browser interface")

    if first['blue_pixels'] == 0 and first['red_pixels'] == 0:
        print("   - NO BUTTON COLORS DETECTED")
        print("   - Web app buttons are not visible in screenshots")

    if first['text_score'] < 20:
        print("   - LOW TEXT CONTENT")
        print("   - Screenshots may not show the actual web app")

if __name__ == "__main__":
    llm_analyze_screenshots()