#!/usr/bin/env python3
"""
Analyze actual colors in the current screenshot
"""

from PIL import Image
import os

def analyze_actual_colors():
    """Analyze what colors are actually present in the current screen"""

    # Take current screenshot
    import pyautogui
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size

    print("🎨 ANALYZING ACTUAL COLORS IN CURRENT SCREENSHOT")
    print("=" * 60)
    print(f"📐 Screenshot size: {width}x{height}")

    if screenshot.mode != 'RGB':
        screenshot = screenshot.mode.convert('RGB')

    # Sample colors in a grid
    color_counts = {}
    button_candidates = []

    for x in range(100, width-100, 50):
        for y in range(100, height-100, 50):
            pixel = screenshot.getpixel((x, y))
            r, g, b = pixel

            # Count color frequencies
            color_key = (r//10*10, g//10*10, b//10*10)  # Round to nearest 10
            color_counts[color_key] = color_counts.get(color_key, 0) + 1

            # Look for button-like colors (saturated colors)
            if (r > 150 or g > 150 or b > 150) and (r < 50 or g < 50 or b < 50):
                # High saturation
                saturation = max(r, g, b) - min(r, g, b)
                if saturation > 100:
                    button_candidates.append((x, y, pixel))

    # Show top colors
    print("\n🎨 TOP 10 MOST COMMON COLORS:")
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    for i, ((r, g, b), count) in enumerate(sorted_colors[:10]):
        percentage = count / sum(color_counts.values()) * 100
        print("2d")

    print(f"\n🔘 FOUND {len(button_candidates)} POTENTIAL BUTTON COLORS:")

    # Group button candidates by color
    button_color_groups = {}
    for x, y, color in button_candidates[:20]:  # Show first 20
        color_key = tuple(color)
        if color_key not in button_color_groups:
            button_color_groups[color_key] = []
        button_color_groups[color_key].append((x, y))

    for color, positions in list(button_color_groups.items())[:5]:
        print(f"   RGB{color}: {len(positions)} pixels at positions like {positions[0]}")

    # Check for Bootstrap-like colors
    bootstrap_colors = {
        'primary_blue': ((0, 123, 255), (13, 110, 253)),
        'success_green': ((25, 135, 84), (40, 167, 69)),
        'danger_red': ((220, 53, 69), (201, 25, 11)),
        'outline_primary': ((13, 110, 253), (13, 110, 253))
    }

    print("\n🔍 CHECKING FOR BOOTSTRAP COLORS:")
    for name, (old_color, new_color) in bootstrap_colors.items():
        # Check if any sampled color is close to these
        for sample_color in color_counts.keys():
            for target_color in [old_color, new_color]:
                distance = sum((a-b)**2 for a, b in zip(sample_color, target_color))**0.5
                if distance < 50:  # Within tolerance
                    count = color_counts[sample_color]
                    print(f"   ✅ {name}: Found RGB{sample_color} (close to RGB{target_color}, {count} pixels)")

    return sorted_colors, button_candidates

if __name__ == "__main__":
    colors, buttons = analyze_actual_colors()