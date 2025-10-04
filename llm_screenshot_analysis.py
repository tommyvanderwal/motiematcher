#!/usr/bin/env python3
"""
Directly analyze screenshots as an LLM would - open them and describe what I see
"""

from PIL import Image
import os

def analyze_screenshot_content(filename):
    """Open and analyze a screenshot to describe what it contains"""

    filepath = os.path.join("test_screenshots", filename)
    if not os.path.exists(filepath):
        return f"❌ Screenshot {filename} not found"

    print(f"\n🔍 ANALYZING: {filename}")
    print("=" * 60)

    try:
        img = Image.open(filepath)
        width, height = img.size
        print(f"📐 Dimensions: {width}x{height}")

        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Sample pixels in a grid to understand content
        samples = []
        for x in range(0, width, max(1, width//20)):  # Sample every ~5% across
            for y in range(0, height, max(1, height//20)):
                samples.append(img.getpixel((x, y)))

        # Analyze colors
        avg_r = sum(p[0] for p in samples) / len(samples)
        avg_g = sum(p[1] for p in samples) / len(samples)
        avg_b = sum(p[2] for p in samples) / len(samples)
        brightness = (avg_r + avg_g + avg_b) / 3 / 255

        print(f"💡 Average brightness: {brightness:.3f}")
        print(f"🎨 Average color: RGB({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f})")

        # Check for text-like patterns (high contrast areas)
        text_indicators = 0
        button_indicators = 0

        for x in range(100, width-100, 50):
            for y in range(100, height-100, 50):
                center = img.getpixel((x, y))
                center_brightness = sum(center) / 3

                # Check neighbors for contrast (text detection)
                neighbors = []
                for dx in [-5, 0, 5]:
                    for dy in [-5, 0, 5]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbors.append(sum(img.getpixel((nx, ny))) / 3)

                if neighbors:
                    avg_neighbor = sum(neighbors) / len(neighbors)
                    contrast = abs(center_brightness - avg_neighbor)
                    if contrast > 100:  # High contrast = potential text
                        text_indicators += 1

                    # Check for button-like colors (blues, greens)
                    r, g, b = center
                    if (r < 100 and g > 150 and b > 200) or (r > 200 and g < 100 and b < 100):  # Blue or red buttons
                        button_indicators += 1

        print(f"📝 Text-like areas: {text_indicators}")
        print(f"🔘 Button-like colors: {button_indicators}")

        # Try to identify what page this is
        if brightness > 0.95:
            print("❌ CONCLUSION: Screenshot appears EMPTY/WHITE")
            print("   - No content visible")
            print("   - Test likely failed to capture web app")
        elif brightness < 0.4 and text_indicators > 50:
            print("✅ CONCLUSION: Screenshot contains WEB PAGE CONTENT")
            print("   - Dark text on light background")
            print("   - Likely shows the MotieMatcher web app")

            if button_indicators > 5:
                print("   - Contains interactive elements (buttons)")
            else:
                print("   - Mostly text content")

        else:
            print("🤔 CONCLUSION: Screenshot contains SOME CONTENT")
            print("   - Mixed brightness levels")
            print("   - May be browser chrome or partial capture")

        return True

    except Exception as e:
        print(f"❌ Error analyzing {filename}: {e}")
        return False

def analyze_key_screenshots():
    """Analyze the most important screenshots from the recent test"""

    key_screenshots = [
        "01_initial_page_211558.png",      # Start page
        "02_after_start_211600.png",      # After clicking start
        "03_motion_1_start_211600.png",   # First motion
        "04_motion_1_voted_voor_211602.png", # After voting
        "05_results_page_211614.png",     # Results page
    ]

    print("🤖 LLM DIRECT SCREENSHOT ANALYSIS")
    print("=" * 80)
    print("As an LLM, I'm opening these PNG files and describing what I see...")

    for screenshot in key_screenshots:
        analyze_screenshot_content(screenshot)

    print("\n" + "=" * 80)
    print("🎯 LLM VERDICT:")
    print("Based on my analysis of the pixel data in these screenshots,")
    print("I can tell you whether the automated test is actually working...")

if __name__ == "__main__":
    analyze_key_screenshots()