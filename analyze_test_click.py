#!/usr/bin/env python3
"""
Analyze the specific test_click_result.png screenshot
"""

from PIL import Image
import os

def analyze_test_click():
    """Analyze the test click result screenshot specifically"""

    filepath = "test_screenshots/test_click_result.png"

    if not os.path.exists(filepath):
        print("❌ test_click_result.png not found")
        return

    print("🔍 ANALYZING TEST CLICK RESULT")
    print("=" * 50)

    img = Image.open(filepath)
    width, height = img.size
    file_size = os.path.getsize(filepath)

    print(f"📐 Resolution: {width}x{height}")
    print(f"📁 File size: {file_size} bytes")

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Check if it's all white/empty
    pixels = []
    for x in range(0, width, 100):  # Sample every 100 pixels
        for y in range(0, height, 100):
            pixels.append(img.getpixel((x, y)))

    # Calculate average brightness
    avg_brightness = sum(sum(p) for p in pixels) / len(pixels) / 3 / 255
    print(f"💡 Average brightness: {avg_brightness:.3f}")

    # Check for any non-white pixels
    non_white_pixels = 0
    dark_pixels = 0
    for pixel in pixels:
        if pixel != (255, 255, 255):
            non_white_pixels += 1
        if sum(pixel) < 400:  # Dark pixel
            dark_pixels += 1

    print(f"🎨 Non-white pixels: {non_white_pixels}/{len(pixels)}")
    print(f"⚫ Dark pixels: {dark_pixels}/{len(pixels)}")

    # Check specific areas where buttons should be
    button_positions = [
        (1440, 910),   # Start button
        (1290, 1060),  # Voor button
        (1590, 1060),  # Tegen button
        (1440, 1600),  # Results button
    ]

    print("\n🎯 CHECKING BUTTON POSITIONS:")
    for i, (x, y) in enumerate(button_positions):
        if 0 <= x < width and 0 <= y < height:
            pixel = img.getpixel((x, y))
            brightness = sum(pixel) / 3 / 255
            print(f"   Button {i+1} ({x},{y}): RGB{pixel} - brightness: {brightness:.2f}")
        else:
            print(f"   Button {i+1} ({x},{y}): OUT OF BOUNDS")

    # Check if this looks like a web page or empty screen
    if avg_brightness > 0.95 and non_white_pixels < len(pixels) * 0.01:
        print("\n❌ CONCLUSION: Screenshot appears to be EMPTY/WHITE")
        print("   - This suggests the click didn't work")
        print("   - Or the screenshot captured the wrong area")
        print("   - Browser might not be where we think it is")
    elif dark_pixels > len(pixels) * 0.1:
        print("\n✅ CONCLUSION: Screenshot contains content")
        print("   - Dark pixels suggest text or UI elements")
        print("   - Click may have worked")
    else:
        print("\n🤔 CONCLUSION: Screenshot is ambiguous")
        print("   - Some content but mostly uniform")

if __name__ == "__main__":
    analyze_test_click()