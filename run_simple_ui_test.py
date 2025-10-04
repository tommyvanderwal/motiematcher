#!/usr/bin/env python3
"""Start the simple FastAPI server and run the smart UI test."""

import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

HOST = "127.0.0.1"
PORT = 8010
BASE_URL = f"http://{HOST}:{PORT}"


def wait_for_server(timeout: float = 15.0) -> bool:
    """Poll the health endpoint until the server responds or timeout."""
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health", timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception as err:
            last_error = err
            time.sleep(0.5)
    if last_error:
        print(f"Server didn't respond in time: {last_error}")
    return False


def start_server() -> subprocess.Popen:
    """Launch uvicorn serving the simple app."""
    uvicorn_cmd = [sys.executable, "-m", "uvicorn", "app.main_simple:app", "--host", HOST, "--port", str(PORT)]
    print("Starting server:", " ".join(uvicorn_cmd))
    return subprocess.Popen(uvicorn_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def run_ui_test():
    """Run the PyAutoGUI smart test."""
    cmd = [sys.executable, "smart_test_improved.py"]
    print("Running UI test:", " ".join(cmd))
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def main():
    server_process = start_server()
    try:
        if not wait_for_server():
            server_process.terminate()
            server_process.wait(timeout=5)
            raise RuntimeError("Server failed to start in time")

        print(f"Opening browser to {BASE_URL}")
        webbrowser.open(BASE_URL)
        time.sleep(5)

        os.environ["MOTIEMATCHER_BASE_URL"] = BASE_URL
        result = run_ui_test()
        print("UI test return code:", result.returncode)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            raise SystemExit("Smart UI test failed")

    finally:
        print("Stopping server...")
        if server_process.poll() is None:
            try:
                server_process.send_signal(signal.SIGINT)
                server_process.wait(timeout=5)
            except Exception:
                server_process.kill()
        if server_process.stdout:
            try:
                output = server_process.stdout.read().decode("utf-8", errors="ignore")
                print("\nServer output:\n", output)
            except Exception:
                pass


if __name__ == "__main__":
    main()
