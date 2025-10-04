#!/usr/bin/env python3
"""Smoke tests for app.main_simple using FastAPI TestClient"""

from fastapi.testclient import TestClient
from app.main_simple import app, get_motions

def run_smoke_tests():
    client = TestClient(app)

    # Start page
    resp_start = client.get("/")
    print("GET / ->", resp_start.status_code)
    assert resp_start.status_code == 200
    assert "Start de Stemwijzer" in resp_start.text

    # Health endpoint
    resp_health = client.get("/health")
    print("GET /health ->", resp_health.status_code, resp_health.json())
    assert resp_health.status_code == 200
    assert resp_health.json().get("status") == "ok"

    # Motions API
    resp_motions = client.get("/api/motions")
    print("GET /api/motions ->", resp_motions.status_code)
    assert resp_motions.status_code == 200
    assert len(resp_motions.json().get("motions", [])) == len(get_motions())

    # Start session
    resp_session = client.post("/start-session", follow_redirects=False)
    print("POST /start-session ->", resp_session.status_code, resp_session.headers.get("location"))
    assert resp_session.status_code in (302, 303)
    location = resp_session.headers["location"]

    # Follow redirect to first motion
    resp_motion = client.get(location)
    print(f"GET {location} ->", resp_motion.status_code)
    assert resp_motion.status_code == 200

    # Submit vote
    motion = get_motions()[0]
    motion_path = location
    vote_resp = client.post(
        f"/vote/{location.split('/')[1]}/0",
        data={"motion_id": motion["id"], "vote": "voor"},
        follow_redirects=False,
    )
    print("POST vote ->", vote_resp.status_code, vote_resp.headers.get("location"))
    assert vote_resp.status_code in (302, 303)

    # Results page
    results_location = vote_resp.headers["location"] if "results" in vote_resp.headers.get("location", "") else f"/{location.split('/')[1]}/results"
    resp_results = client.get(results_location)
    print(f"GET {results_location} ->", resp_results.status_code)
    assert resp_results.status_code == 200
    assert "Jouw keuze" in resp_results.text

if __name__ == "__main__":
    run_smoke_tests()
    print("Smoke tests passed.")
