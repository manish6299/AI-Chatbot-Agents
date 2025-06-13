from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
from ai_agent import get_response_from_ai_agent

import threading
import subprocess
import os

ALLOWED_MODEL_NAMES = [
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "llama-3.3-70b-versatile",
    "gpt-4o-mini",
]

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[str]
    allow_search: bool

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

@app.get("/")
def root():
    # Redirect root to Streamlit app
    return RedirectResponse(url="/streamlit")

def run_streamlit():
    # Streamlit runs on the same port, exposed via proxy
    subprocess.run([
        "streamlit", "run", "frontend.py",
        "--server.port", os.getenv("PORT", "8080"),
        "--server.address", "0.0.0.0"
    ])

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=run_streamlit, daemon=True)
    thread.start()
