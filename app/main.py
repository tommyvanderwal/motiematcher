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
DATA_FILE = "final_filtered_data.json"
SESSIONS_DIR = "app/sessions"

# Ensure sessions directory exists
os.makedirs(SESSIONS_DIR, exist_ok=True)


# --- Data Loading & Caching ---
@lru_cache()
def get_motions():
    """
    Loads, de-duplicates, and processes motion data.
    The result is cached for performance.
    """
    if not os.path.exists(DATA_FILE):
        return []

    df = pd.read_json(DATA_FILE)
    
    # --- De-duplication Logic ---
    # Keep only the first occurrence of each unique 'Matched_Zaak_Id'
    df_unique = df.drop_duplicates(subset=['Matched_Zaak_Id'], keep='first')

    print(f"Original motions: {len(df)}, Unique motions: {len(df_unique)}")

    motions = []
    for _, row in df_unique.iterrows():
        stemverdeling = row.get('Stemverdeling', [])
        if isinstance(stemverdeling, float):
            # Safety guard in case the column is missing or NaN
            stemverdeling = []

        if isinstance(stemverdeling, float):
            stemverdeling = []

        gerelateerde_besluit_ids = row.get('Gerelateerde_Besluit_Ids', [])
        if isinstance(gerelateerde_besluit_ids, float):
            gerelateerde_besluit_ids = []

        motions.append({
            "id": row['Besluit_Id'],
            "zaak_id": row.get('Matched_Zaak_Id'),
            "onderwerp": row.get('Matched_Zaak_Onderwerp', 'Geen onderwerp gevonden'),
            "besluit_tekst": row.get('BesluitTekst', ''),
            "totaal_voor": row.get('Totaal_Voor', 0),
            "totaal_tegen": row.get('Totaal_Tegen', 0),
            "verschil": row.get('Verschil', 0),
            "stemverdeling": stemverdeling,
            "gerelateerde_besluit_ids": gerelateerde_besluit_ids,
        })
    return motions

@lru_cache()
def get_full_motion_text(zaak_id: str) -> str:
    """
    Retrieves the full text of a motion based on its zaak_id.
    """
    motions = get_motions()
    for motion in motions:
        if motion.get("zaak_id") == zaak_id:
            return motion.get("besluit_tekst", "")
    return ""

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
    zaak_id = current_motion.get("zaak_id")
    full_text = get_full_motion_text(zaak_id) if zaak_id else "Volledige tekst niet beschikbaar."

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
        "motion.html",
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
    form = await request.form()
    motion_id = form.get('motion_id')
    user_vote = form.get('vote')

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
        resultaat = {
            "onderwerp": motion.get("onderwerp"),
            "besluit_tekst": motion.get("besluit_tekst"),
            "totaal_voor": motion.get("totaal_voor"),
            "totaal_tegen": motion.get("totaal_tegen"),
            "verschil": motion.get("verschil"),
            "stemverdeling": motion.get("stemverdeling", []),
            "gerelateerde_besluit_ids": motion.get("gerelateerde_besluit_ids", []),
            "user_vote": session_data.get("user_votes", {}).get(motion_id)
        }
        results.append(resultaat)

    return templates.TemplateResponse(
        "results.html", 
        {"request": request, "session_id": session_id, "results": results}
    )

# To run this app:
# uvicorn app.main:app --reload
