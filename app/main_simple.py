import json
import uuid
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- App Configuration ---
app = FastAPI()

# Mount static files (for CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "final_linked_data.json"
SESSIONS_DIR = BASE_DIR / "app" / "sessions"

# Ensure sessions directory exists
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# --- Data Loading ---
MOTION_LIMIT = 5
MIN_PARTIES = 3
VALID_VOTE_TYPES = {"voor", "tegen", "onthouding"}


def _normalise_vote(value: str) -> str:
    return str(value or "").strip().lower()


@lru_cache(maxsize=1)
def get_motions():
    """Load real motions with aggregated vote distributions."""
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as handle:
        records = json.load(handle)

    grouped = {}

    for record in records:
        besluit_id = record.get("Besluit_Id") or record.get("Id_besluit")
        if not besluit_id:
            continue

        vote_type = _normalise_vote(record.get("Soort"))
        if vote_type not in VALID_VOTE_TYPES:
            continue

        actor = record.get("ActorNaam")
        if not actor:
            continue

        try:
            seats = int(record.get("FractieGrootte") or 0)
        except (TypeError, ValueError):
            seats = 0

        motion = grouped.setdefault(
            besluit_id,
            {
                "id": besluit_id,
                "zaak_id": record.get("Matched_Zaak_Id"),
                "onderwerp": record.get("Matched_Zaak_Onderwerp") or "Onbekend onderwerp",
                "besluit_tekst": record.get("BesluitTekst") or "",
                "besluit_soort": record.get("BesluitSoort") or "",
                "totaal_voor": 0,
                "totaal_tegen": 0,
                "totaal_onthouding": 0,
                "stemverdeling": [],
                "gerelateerde_besluit_ids": record.get("Gerelateerde_Besluit_Ids") or [],
            },
        )

        motion["stemverdeling"].append(
            {
                "ActorNaam": actor,
                "Soort_stemming": vote_type.capitalize(),
                "FractieGrootte": seats,
            }
        )

        if vote_type == "voor":
            motion["totaal_voor"] += seats
        elif vote_type == "tegen":
            motion["totaal_tegen"] += seats
        else:
            motion["totaal_onthouding"] += seats

    motions = []
    for motion in grouped.values():
        if not motion["stemverdeling"]:
            continue

        motion["stemverdeling"].sort(key=lambda item: item["ActorNaam"])
        motion["verschil"] = abs(motion["totaal_voor"] - motion["totaal_tegen"])
        motions.append(motion)

    motions.sort(
        key=lambda item: (len(item["stemverdeling"]), item["totaal_voor"] + item["totaal_tegen"]),
        reverse=True,
    )

    selected = []
    seen_ids = set()

    for motion in motions:
        if len(motion["stemverdeling"]) >= MIN_PARTIES:
            selected.append(motion)
            seen_ids.add(motion["id"])
        if len(selected) >= MOTION_LIMIT:
            break

    if len(selected) < MOTION_LIMIT:
        for motion in motions:
            if motion["id"] in seen_ids:
                continue
            selected.append(motion)
            if len(selected) >= MOTION_LIMIT:
                break

    return selected


def get_full_motion_text(zaak_nummer: str) -> str:
    """Return the besluit text for a given zaak."""
    for motion in get_motions():
        if motion.get("zaak_id") == zaak_nummer:
            return motion.get("besluit_tekst", "")
    return ""

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def start_page(request: Request):
    """Shows a start page that initiates the session."""
    return templates.TemplateResponse("start.html", {"request": request})

@app.post("/start-session", response_class=RedirectResponse)
async def start_session():
    """Creates a new session and redirects to the first motion."""
    session_id = str(uuid.uuid4())
    session_file = SESSIONS_DIR / f"{session_id}.json"

    # Create an empty session file
    with session_file.open('w', encoding='utf-8') as f:
        json.dump({"user_votes": {}}, f)

    # Redirect to the first motion
    return RedirectResponse(url=f"/{session_id}/motion/0", status_code=303)

@app.get("/{session_id}/motion/{motion_index}", response_class=HTMLResponse)
async def show_motion(request: Request, session_id: str, motion_index: int):
    """Shows a specific motion for voting."""
    motions = get_motions()
    if motion_index >= len(motions):
        # All motions answered, redirect to results
        return RedirectResponse(url=f"/{session_id}/results", status_code=303)

    current_motion = motions[motion_index]
    zaak_nummer = current_motion.get("zaak_id")
    full_text = get_full_motion_text(zaak_nummer) if zaak_nummer else "Volledige tekst niet beschikbaar."

    session_file = SESSIONS_DIR / f"{session_id}.json"
    user_votes = {}
    if session_file.exists():
        with session_file.open('r', encoding='utf-8') as f:
            session_data = json.load(f)
            user_votes = session_data.get("user_votes", {})

    current_vote = user_votes.get(current_motion.get("id"))
    total_motions = len(motions)
    progress_percent = int(((motion_index + 1) / max(total_motions, 1)) * 100)

    return templates.TemplateResponse(
        "motion_improved.html",
        {
            "request": request,
            "motion": current_motion,
            "motion_index": motion_index,
            "total_motions": total_motions,
            "progress_percent": progress_percent,
            "session_id": session_id,
            "user_vote": current_vote,
            "full_text": full_text
        }
    )

@app.post("/vote/{session_id}/{motion_index}", response_class=RedirectResponse)
async def handle_vote(session_id: str, motion_index: int, request: Request):
    """Handles a user's vote, saves it, and redirects to the next motion."""
    try:
        form = await request.form()
        motion_id = form.get('motion_id')
        user_vote = form.get('vote')

        if not motion_id or not user_vote:
            return JSONResponse(content={"error": "Ontbrekende form data"}, status_code=400)

        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            return JSONResponse(content={"error": "Sessie niet gevonden"}, status_code=404)

        with session_file.open('r+', encoding='utf-8') as f:
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
    """Shows the results of the voting session."""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        return HTMLResponse(content="Sessie niet gevonden", status_code=404)

    with session_file.open('r', encoding='utf-8') as f:
        session_data = json.load(f)

    motions = get_motions()
    user_votes = session_data.get("user_votes", {})

    results = []
    for motion in motions:
        motion_id = motion.get("id")
        user_vote = user_votes.get(motion_id)
        if user_vote:
            user_vote_display = user_vote.capitalize()
        else:
            user_vote_display = None

        results.append({
            "id": motion_id,
            "onderwerp": motion.get("onderwerp"),
            "besluit_tekst": motion.get("besluit_tekst"),
            "totaal_voor": motion.get("totaal_voor"),
            "totaal_tegen": motion.get("totaal_tegen"),
            "verschil": motion.get("verschil"),
            "stemverdeling": motion.get("stemverdeling", []),
            "gerelateerde_besluit_ids": motion.get("gerelateerde_besluit_ids", []),
            "user_vote": user_vote_display,
            "besluit_soort": motion.get("besluit_soort", "Unknown")
        })

    party_stats = {}
    for motion in motions:
        motion_id = motion.get("id")
        user_vote = user_votes.get(motion_id)
        if not user_vote:
            continue

        for party_vote in motion.get("stemverdeling", []):
            party_name = party_vote.get("ActorNaam")
            vote_type = _normalise_vote(party_vote.get("Soort_stemming"))
            if not party_name or vote_type not in VALID_VOTE_TYPES:
                continue

            stats = party_stats.setdefault(party_name, {"matches": 0, "total": 0})
            stats["total"] += 1
            if vote_type == user_vote:
                stats["matches"] += 1

    party_alignment = []
    for party_name, stats in party_stats.items():
        total = stats.get("total", 0)
        if total == 0:
            continue
        matches = stats.get("matches", 0)
        percentage = round((matches / total) * 100, 1)
        party_alignment.append({
            "party": party_name,
            "matches": matches,
            "total": total,
            "percentage": percentage
        })

    party_alignment.sort(key=lambda item: (item["percentage"], item["matches"]), reverse=True)

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "session_id": session_id,
            "results": results,
            "party_alignment": party_alignment,
            "total_votes_cast": sum(1 for vote in user_votes.values() if vote),
        }
    )


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Simple health endpoint for uptime checks."""
    return {"status": "ok", "motions": len(get_motions())}


@app.get("/api/motions", response_class=JSONResponse)
async def list_motions():
    """Expose the demo motions as JSON for automated testers."""
    return {"motions": get_motions()}