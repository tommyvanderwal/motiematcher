from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


def main() -> None:
    with TestClient(app) as client:
        response = client.post("/start-session", follow_redirects=False)
        if response.status_code not in (302, 303, 307, 308):
            response.raise_for_status()
        location = response.headers["location"]
        print(f"Redirected to: {location}")

        visited = []
        motion_url = location
        while motion_url:
            motion_response = client.get(motion_url, follow_redirects=False)
            print(f"Visited {motion_url} -> {motion_response.status_code}")
            if motion_response.status_code >= 500:
                print(motion_response.text)
                break

            visited.append(motion_url)

            # After a GET, request next motion (simulate vote action without posting)
            motion_index = int(motion_url.rstrip('/').split('/')[-1])
            next_index = motion_index + 1
            if next_index >= 3:
                break
            motion_url = f"/{location.strip('/').split('/')[0]}/motion/{next_index}"

        print("Visited pages:", visited)


if __name__ == "__main__":
    main()
