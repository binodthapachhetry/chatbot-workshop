import os
import uuid

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from app.inference import generate_reply
from app.logging_utils import log_interaction

app = FastAPI(title="Workshop Chatbot")

# Serve static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("frontend/index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    reply = generate_reply(request.message)

    try:
        log_interaction(
            session_id=session_id,
            user_message=request.message,
            bot_response=reply,
            meta={"app_version": os.getenv("APP_VERSION", "dev")},
        )
    except Exception as e:
        print(f"[WARN] Failed to log interaction: {e}")

    return ChatResponse(response=reply, session_id=session_id)


@app.get("/health")
async def health():
    return {"status": "ok", "app_version": os.getenv("APP_VERSION", "dev")}