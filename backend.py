# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from ai_agent import get_response_from_ai_agent

import subprocess
import threading
import os

# Pydantic model
class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[str]
    allow_search: bool

ALLOWED_MODEL_NAMES = [
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "llama-3.3-70b-versatile",
    "gpt-4o-mini",
]

app = FastAPI(title="LangGraph AI Agent")

@app.post("/messages")
def chat_endpoint(request: RequestState):
    if request.model_name not in ALLOWED_MODEL_NAMES:
        return {"error": "Invalid model name. Kindly select a valid AI model"}

    response = get_response_from_ai_agent(
        request.model_name,
        request.messages,
        request.allow_search,
        request.system_prompt,
        request.model_provider
    )
    return response

# Launch Streamlit in a thread
def run_streamlit():
    port = int(os.getenv("STREAMLIT_PORT", 8501))
    subprocess.run([
        "streamlit", "run", "frontend.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0"
    ])

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=run_streamlit, daemon=True)
    thread.start()

# No __main__ block needed — Railway runs via Procfile
