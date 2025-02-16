import datetime
import json
import httpx
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
#uvicorn main:app --reload

# Blockchain API Node
CONNECTED_SERVICE_ADDRESS = "http://127.0.0.1:8000"

# Sample Voter Data
POLITICAL_PARTIES = ["INC", "BJP", "AAP", "CPI","NOTA"]
VOTER_IDS = ["VOID001", "VOID002", "VOID003", "VOID004", "VOID005", "VOID006",
             "VOID007", "VOID008", "VOID009", "VOID010", "VOID011", "VOID012",
             "VOID013", "VOID014", "VOID015"]

vote_check = []  # Track Voter IDs that have already voted
posts = []  # Store blockchain transactions

router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def fetch_posts():
    """Fetch transactions from blockchain and update post list."""
    global posts
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONNECTED_SERVICE_ADDRESS}/chain")
        if response.status_code == 200:
            content = []
            chain = response.json()
            for block in chain["chain"]:
                for tx in block["transactions"]:
                    tx["index"] = block["index"]
                    tx["hash"] = block["previous_hash"]
                    content.append(tx)

            posts = sorted(content, key=lambda k: k["timestamp"], reverse=True)

@router.get("/")
async def index(request: Request):
    """Render the main voting page."""
    await fetch_posts()
    vote_gain = [post["party"] for post in posts]

    messages = request.session.pop("flash_messages", [])  # Retrieve flash messages

    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "E-voting System using Blockchain & FastAPI",
        "posts": posts,
        "vote_gain": vote_gain,
        "node_address": CONNECTED_SERVICE_ADDRESS,
        "readable_time": timestamp_to_string,
        "political_parties": POLITICAL_PARTIES,
        "voter_ids": VOTER_IDS,
        "messages": messages  # Pass flash messages to template
    })

@router.post("/submit")
async def submit_vote(request: Request, voter_id: str = Form(...), party: str = Form(...)):
    """Handle vote submission."""
    if voter_id not in VOTER_IDS:
        request.session.setdefault("flash_messages", []).append(('error',"❌ Invalid Voter ID! Please select a valid voter ID."))
        return RedirectResponse("/", status_code=303)

    if voter_id in vote_check:
        request.session.setdefault("flash_messages", []).append(('error',f"❌ Voter ID ({voter_id}) has already voted! One vote per ID."))
        return RedirectResponse("/", status_code=303)

    vote_check.append(voter_id)
    post_object = {"voter_id": voter_id, "party": party}

    async with httpx.AsyncClient() as client:
        await client.post(f"{CONNECTED_SERVICE_ADDRESS}/new_transaction", json=post_object)

    request.session.setdefault("flash_messages", []).append(('success',f"✅ Voted for {party} successfully!"))
    return RedirectResponse("/", status_code=303)

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%d %H:%M")
