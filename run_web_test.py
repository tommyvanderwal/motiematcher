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

    # Run the server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(host, port))
    server_thread.daemon = True
    server_thread.start()

    # Give the server a moment to start
    time.sleep(3)

    # Open the web browser to the correct URL
    url = f"http://{host}:{port}"
    print(f"Opening browser to {url}")
    webbrowser.open(url)

    # Let the server run for 30 seconds for testing
    print("Server will stop automatically in 30 seconds...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("Stopping server manually.")
    
    print("Test time finished. Stopping server.")
    # The script will exit here, and because the server thread is a daemon, it will be terminated.
    # In a real scenario, you would need a more graceful shutdown mechanism.
    os._exit(0)
