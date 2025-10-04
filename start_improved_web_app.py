#!/usr/bin/env python3
"""
Improved MotieMatcher Web App Launcher
Uses the enhanced main_improved.py with better data loading and UI
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("🚀 Starting Improved MotieMatcher Web App...")

    # Change to the app directory
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    os.chdir(app_dir)

    # Check if improved main file exists
    main_file = 'main_improved.py'
    if not os.path.exists(main_file):
        print(f"❌ Error: {main_file} not found in {app_dir}")
        sys.exit(1)

    # Check if templates exist
    template_dir = 'templates'
    required_templates = ['start.html', 'motion_improved.html', 'results.html']
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if not os.path.exists(template_path):
            print(f"⚠️  Warning: Template {template} not found")

    print("📊 Loading current parliament motion data...")
    print("🌐 Starting FastAPI server...")

    try:
        # Start the server
        cmd = [sys.executable, main_file]
        process = subprocess.Popen(cmd, cwd=app_dir)

        # Wait a moment for server to start
        time.sleep(3)

        # Check if server is running
        if process.poll() is None:
            print("✅ Server started successfully!")
            print("🌍 Opening web app in browser...")

            # Open browser
            webbrowser.open('http://127.0.0.1:51043')

            print("\n📋 Instructions:")
            print("- The app will show recent parliamentary motions")
            print("- Vote 'Voor' or 'Tegen' on each motion")
            print("- View your results compared to parliament")
            print("- UUIDs are now hidden for cleaner interface")
            print("- Full motion texts are loaded where available")

            print("\n🛑 Press Ctrl+C to stop the server")

            # Keep running until interrupted
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")

        else:
            print("❌ Failed to start server")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()