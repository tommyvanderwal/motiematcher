#!/usr/bin/env python3
"""
Open screenshots for LLM inspection and create better clicking strategy
"""

import os
import subprocess
import time
from PIL import Image

def open_screenshots_for_inspection():
    """Open recent screenshots so LLM can see what's actually happening"""

    screenshots_dir = "test_screenshots"
    if not os.path.exists(screenshots_dir):
        print("❌ No screenshots directory")
        return

    # Get recent screenshots
    all_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
    recent_files = [f for f in all_files if '_211' in f]  # Today's screenshots
    recent_files.sort()

    if not recent_files:
        print("❌ No recent screenshots found")
        return

    print(f"🖼️  Opening {len(recent_files)} screenshots for inspection...")
    print("As LLM, I need to SEE these to understand the clicking problems")

    # Open first few screenshots
    for i, filename in enumerate(recent_files[:3], 1):
        filepath = os.path.join(screenshots_dir, filename)
        print(f"📸 Opening: {filename}")

        try:
            # Open with default Windows viewer
            subprocess.run(["start", filepath], shell=True, check=True)
            time.sleep(1)  # Brief pause between openings
        except Exception as e:
            print(f"❌ Could not open {filename}: {e}")

    print("\n✅ Screenshots opened for inspection")
    return recent_files[:3]

def analyze_webpage_layout():
    """Analyze what the web app should look like based on templates"""

    print("\n🔍 ANALYZING WEB APP LAYOUT:")
    print("=" * 50)

    print("📄 START PAGE (start.html):")
    print("   - Centered layout with vh-100")
    print("   - Large 'Start de Stemwijzer' button (btn-primary btn-lg)")
    print("   - Blue Bootstrap button")

    print("\n📄 MOTION PAGE (motion_improved.html):")
    print("   - Progress bar at top")
    print("   - Motion text in scrollable container")
    print("   - Large green 'Voor' button (btn-success btn-lg)")
    print("   - Large red 'Tegen' button (btn-danger btn-lg)")
    print("   - 'Resultaten bekijken' button (btn-outline-primary)")

    print("\n🎯 EXPECTED BUTTON POSITIONS:")
    print("   Start button: Center of screen")
    print("   Voor button: Left side, lower half")
    print("   Tegen button: Right side, lower half")
    print("   Results button: Center bottom")

def create_better_clicking_strategy():
    """Create a better strategy for clicking based on web app layout"""

    print("\n🎯 CREATING BETTER CLICKING STRATEGY:")
    print("=" * 50)

    print("🔧 PROBLEMS IDENTIFIED:")
    print("   1. Browser window detection may be failing")
    print("   2. Hardcoded coordinates don't account for browser chrome")
    print("   3. Screenshots show gray browser interface, not web content")
    print("   4. No blue/red button colors detected in screenshots")

    print("\n💡 BETTER STRATEGY:")
    print("   1. Use image recognition to find buttons by color")
    print("   2. Look for blue pixels (start button)")
    print("   3. Look for green pixels (Voor button)")
    print("   4. Look for red pixels (Tegen button)")
    print("   5. Calculate relative positions from detected elements")

    print("\n📋 TO-DO ITEMS FOR FIXING:")
    print("   ✅ Detect browser window boundaries properly")
    print("   ✅ Find web content area (skip browser chrome)")
    print("   ✅ Use color-based button detection")
    print("   ✅ Implement relative coordinate system")
    print("   ✅ Add visual feedback for click targets")
    print("   ✅ Test with actual web app running")

def inspect_ui_issues():
    """Look for UI/UX issues in the web app design"""

    print("\n🔍 UI/UX ISSUES FOUND IN TEMPLATES:")
    print("=" * 50)

    print("⚠️  ISSUES IN motion_improved.html:")
    print("   1. FontAwesome icons referenced but kit not loaded properly")
    print("   2. 'your-fontawesome-kit.js' placeholder in script tag")
    print("   3. Mixed Bootstrap versions (5.1.3 vs 5.3.2)")
    print("   4. No error handling for missing motion data")
    print("   5. Session ID shown in UI (privacy concern)")

    print("\n⚠️  ISSUES IN start.html:")
    print("   1. References to non-existent static/styles.css")
    print("   2. No loading state for form submission")

    print("\n📋 TO-DO ITEMS FOR UI FIXES:")
    print("   - Fix FontAwesome integration")
    print("   - Standardize Bootstrap version")
    print("   - Add proper error handling")
    print("   - Hide sensitive session data")
    print("   - Add loading states")
    print("   - Create proper static/styles.css")

if __name__ == "__main__":
    print("🤖 LLM SCREENSHOT INSPECTION & STRATEGY PLANNING")
    print("=" * 60)

    # Open screenshots for inspection
    opened_files = open_screenshots_for_inspection()

    # Analyze web app layout
    analyze_webpage_layout()

    # Create better clicking strategy
    create_better_clicking_strategy()

    # Inspect UI issues
    inspect_ui_issues()

    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Look at the opened screenshots")
    print("2. Note where buttons should be vs where they appear")
    print("3. Implement color-based button detection")
    print("4. Fix UI issues found in templates")
    print("5. Test the improved clicking strategy")