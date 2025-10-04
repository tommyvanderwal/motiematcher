import uvicorn
import webbrowser
import threading
import time
import os
import socket

def find_available_port(default_port: int = 8000) -> int:
    """Find an available TCP port, preferring the default."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        if sock.connect_ex(("127.0.0.1", default_port)) != 0:
            return default_port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
        temp_socket.bind(("127.0.0.1", 0))
        return temp_socket.getsockname()[1]


def run_server(host: str, port: int):
    """Starts the Uvicorn server."""
    # We need to change the working directory so uvicorn can find the app
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("app.main:app", host=host, port=port, log_level="info")

if __name__ == "__main__":
    host = "127.0.0.1"
    port = find_available_port(8000)

    print(f"🚀 Starting MotieMatcher web application on http://{host}:{port}")
    print("📱 The app will stay running - you can test and take screenshots")
    print("🔄 Press Ctrl+C to stop the server")

    # Run the server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(host, port))
    server_thread.daemon = True
    server_thread.start()

    # Give the server a moment to start
    time.sleep(3)

    # Open the web browser to the correct URL
    url = f"http://{host}:{port}"
    print(f"🌐 Opening browser to {url}")
    webbrowser.open(url)

    print("\n" + "="*60)
    print("🎯 MOTIEMATCHER IS NU ACTIEF!")
    print("="*60)
    print("📋 Wat je kunt doen:")
    print("   • Klik door moties en stem (Voor/Tegen)")
    print("   • Bekijk resultaten aan het einde")
    print("   • Maak screenshots van de interface")
    print("   • Test alle functionaliteit")
    print("="*60)

    # Keep the server running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        os._exit(0)