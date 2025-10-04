import os
import json
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from functools import lru_cache

# --- App Configuration ---
app = FastAPI()

# Mount static files (for CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Define paths
SESSIONS_DIR = "app/sessions"

# Ensure sessions directory exists
os.makedirs(SESSIONS_DIR, exist_ok=True)

# --- Data Loading & Caching ---
@lru_cache()
def get_motions():
    """
    Loads motion data from our current parliament collection.
    """
    motions = []

    # Load from our collected current parliament data
    zaak_file = 'bronnateriaal-onbewerkt/zaak_current/zaak_voted_motions_20251003_200218.json'
    besluit_file = 'bronnateriaal-onbewerkt/besluit_current/besluit_voted_motions_20251003_200218.json'
    stemming_file = 'bronnateriaal-onbewerkt/stemming_current/stemming_voted_motions_20251003_200218.json'

    if not os.path.exists(zaak_file):
        return []

    with open(zaak_file, 'r', encoding='utf-8') as f:
        zaken = json.load(f)

    with open(besluit_file, 'r', encoding='utf-8') as f:
        besluiten = json.load(f)

    with open(stemming_file, 'r', encoding='utf-8') as f:
        stemmingen = json.load(f)

    # Group votes by decision
    votes_by_decision = {}
    for stemming in stemmingen:
        besluit_id = stemming.get('Besluit_Id')
        if besluit_id:
            if besluit_id not in votes_by_decision:
                votes_by_decision[besluit_id] = []
            votes_by_decision[besluit_id].append(stemming)

    # Create motion objects
    for besluit in besluiten:
        besluit_id = besluit.get('Id')
        votes = votes_by_decision.get(besluit_id, [])

        # Count votes
        voor_count = sum(1 for v in votes if v.get('Soort') == 'Voor')
        tegen_count = sum(1 for v in votes if v.get('Soort') == 'Tegen')

        # Find related zaak
        zaak_info = None
        for zaak in zaken[:50]:  # Limit search for performance
            # This is a simplified linkage - in reality we'd need proper linking
            if zaak.get('GewijzigdOp', '').startswith('2025-10'):
                zaak_info = zaak
                break

        if not zaak_info:
            continue

        motions.append({
            "id": besluit_id,
            "zaak_id": zaak_info.get('Nummer', 'Unknown'),
            "onderwerp": zaak_info.get('Titel', 'Geen onderwerp')[:100],
            "besluit_tekst": besluit.get('BesluitTekst', ''),
            "totaal_voor": voor_count,
            "totaal_tegen": tegen_count,
            "verschil": voor_count - tegen_count,
            "stemverdeling": [
                {
                    "ActorNaam": v.get('ActorFractie', 'Unknown'),
                    "Soort_stemming": v.get('Soort', 'Unknown'),
                    "FractieGrootte": v.get('FractieGrootte', 1)
                } for v in votes[:10]  # Show first 10 votes
            ],
            "gerelateerde_besluit_ids": [],
            "besluit_soort": besluit.get('BesluitSoort', 'Unknown')
        })

    print(f"Loaded {len(motions)} motions from current parliament data")
    return motions[:50]  # Limit to 50 for testing

@lru_cache()
def get_full_motion_text(zaak_nummer: str) -> str:
    """
    Retrieves the full text of a motion based on its zaak_nummer.
    """
    # Try to find in document data
    doc_dir = 'bronnateriaal-onbewerkt/document'
    if os.path.exists(doc_dir):
        for filename in os.listdir(doc_dir)[:10]:  # Check first 10 files
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(doc_dir, filename), 'r', encoding='utf-8') as f:
                        docs = json.load(f)
                        for doc in docs[:50]:  # Check first 50 docs
                            if doc.get('DocumentNummer') == zaak_nummer:
                                return doc.get('Inhoud', '')[:2000]  # Limit text length
                except:
                    continue

    return "Volledige tekst niet beschikbaar in huidige dataset. Alleen besluit tekst beschikbaar."

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def start_page(request: Request):
    """
    Shows a start page that initiates the session.
    """
    return templates.TemplateResponse("start.html", {"request": request})


@app.post("/start-session", response_class=RedirectResponse)
async def start_session():
    """
    Creates a new session and redirects to the first motion.
    """
    session_id = str(uuid.uuid4())
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")

    # Create an empty session file
    with open(session_file, 'w') as f:
        json.dump({"user_votes": {}}, f)

    # Redirect to the first motion
    return RedirectResponse(url=f"/{session_id}/motion/0", status_code=303)


@app.get("/{session_id}/motion/{motion_index}", response_class=HTMLResponse)
async def show_motion(request: Request, session_id: str, motion_index: int):
    """
    Shows a specific motion for voting.
    """
    motions = get_motions()
    if motion_index >= len(motions):
        # All motions answered, redirect to results
        return RedirectResponse(url=f"/{session_id}/results", status_code=303)

    current_motion = motions[motion_index]
    zaak_nummer = current_motion.get("zaak_id")
    full_text = get_full_motion_text(zaak_nummer) if zaak_nummer else "Volledige tekst niet beschikbaar."

    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    user_votes = {}
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            user_votes = session_data.get("user_votes", {})

    current_vote = user_votes.get(current_motion.get("id"))
    total_motions = len(motions)
    progress_percent = int(((motion_index + 1) / max(total_motions, 1)) * 100)
    session_url = request.url_for(
        "show_motion",
        session_id=session_id,
        motion_index=motion_index
    )

    return templates.TemplateResponse(
        "motion_improved.html",
        {
            "request": request,
            "motion": current_motion,
            "motion_index": motion_index,
            "total_motions": total_motions,
            "progress_percent": progress_percent,
            "session_id": session_id,
            "session_url": session_url,
            "user_vote": current_vote,
            "full_text": full_text
        }
    )


@app.post("/vote/{session_id}/{motion_index}", response_class=RedirectResponse)
async def handle_vote(session_id: str, motion_index: int, request: Request):
    """
    Handles a user's vote, saves it, and redirects to the next motion.
    """
    try:
        form = await request.form()
        motion_id = form.get('motion_id')
        user_vote = form.get('vote')

        if not motion_id or not user_vote:
            return JSONResponse(content={"error": "Ontbrekende form data"}, status_code=400)

        session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        if not os.path.exists(session_file):
            return JSONResponse(content={"error": "Sessie niet gevonden"}, status_code=404)

        with open(session_file, 'r+') as f:
            session_data = json.load(f)
            session_data.setdefault("user_votes", {})[motion_id] = user_vote
            f.seek(0)
            json.dump(session_data, f, indent=4)
            f.truncate()

        # Redirect to the next motion
        next_index = motion_index + 1
        motions = get_motions()
        if next_index >= len(motions):
            return RedirectResponse(url=f"/{session_id}/results", status_code=303)

        return RedirectResponse(url=f"/{session_id}/motion/{next_index}", status_code=303)

    except Exception as e:
        print(f"Error in handle_vote: {e}")
        return JSONResponse(content={"error": f"Server error: {str(e)}"}, status_code=500)


@app.get("/{session_id}/results", response_class=HTMLResponse)
async def show_results(request: Request, session_id: str):
    """
    Shows the results of the voting session.
    """
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if not os.path.exists(session_file):
        return HTMLResponse(content="Sessie niet gevonden", status_code=404)

    with open(session_file, 'r') as f:
        session_data = json.load(f)

    motions = get_motions()
    results = []
    for motion in motions:
        motion_id = motion.get("id")
        user_vote = session_data.get("user_votes", {}).get(motion_id)
        results.append({
            "onderwerp": motion.get("onderwerp"),
            "besluit_tekst": motion.get("besluit_tekst"),
            "totaal_voor": motion.get("totaal_voor"),
            "totaal_tegen": motion.get("totaal_tegen"),
            "verschil": motion.get("verschil"),
            "stemverdeling": motion.get("stemverdeling", []),
            "gerelateerde_besluit_ids": motion.get("gerelateerde_besluit_ids", []),
            "user_vote": user_vote,
            "besluit_soort": motion.get("besluit_soort", "Unknown")
        })

    return templates.TemplateResponse(
        "results.html",
        {"request": request, "session_id": session_id, "results": results}
    )