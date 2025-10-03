#!/usr/bin/env python3
"""
Master setup script for MotieMatcher data quality fixes
Handles all data quality tasks: analysis and besluit retry
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n[*] {description}")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def setup_environment():
    """Setup Python environment and install dependencies"""
    print("[*] SETTING UP MOTIEMATCHER ENVIRONMENT")
    print("=" * 50)

    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("[!] Not in a virtual environment. Please activate venv first:")
        print("   py -m venv venv")
        print("   venv\\Scripts\\activate")
        return False

    # Install requirements
    if Path("requirements.txt").exists():
        success = run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "Installing Python dependencies"
        )
        if not success:
            return False

    # Install minimal requirements if main requirements fail
    elif Path("requirements-minimal.txt").exists():
        success = run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-minimal.txt"],
            "Installing minimal Python dependencies"
        )
        if not success:
            return False

    return True

def run_task(script_name, task_description):
    """Run a specific task script"""
    print(f"\n{task_description}")
    print("=" * 50)

    script_path = Path(script_name)
    if not script_path.exists():
        print(f"[-] Script not found: {script_name}")
        return False

    success = run_command(
        [sys.executable, script_name],
        f"Running {script_name}"
    )

    return success

def main():
    """Main setup and task runner"""
    parser = argparse.ArgumentParser(description="MotieMatcher Data Quality Fix Runner")
    parser.add_argument(
        "task",
        choices=["analysis", "besluit-retry", "all"],
        help="Task to run: analysis (persoon data), besluit-retry (fix 500 error), or all"
    )

    args = parser.parse_args()

    print("[*] MOTIEMATCHER DATA QUALITY FIXES")
    print("=" * 50)
    print(f"Task: {args.task}")
    print()

    # Setup environment first
    if not setup_environment():
        print("\n[-] Environment setup failed!")
        return 1

    success = True

    if args.task in ["analysis", "all"]:
        success &= run_task(
            "analyze_persoon_structure.py",
            "[*] ANALYZING PERSON DATA STRUCTURE"
        )

    if args.task in ["besluit-retry", "all"]:
        # Create and run besluit retry
        success &= run_task(
            "run_besluit_retry.py",
            "[*] RETRYING BESLUIT COLLECTION"
        )

    if success:
        print("\n[+] ALL REQUESTED TASKS COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("\n[-] SOME TASKS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())