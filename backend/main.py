import os
import logging
from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    logger.error("GEMINI_API_KEY is missing.")

app = FastAPI(title="AI Study Assistant", version="1.2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models (Pydantic v2) ---
class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=5000)
    # Using 'pattern' instead of 'regex' for Pydantic v2
    type: str = Field(..., pattern="^(10mark|20mark|summarize|explain)$")

    @field_validator('prompt')
    @classmethod
    def prevent_empty_prompts(cls, v: str):
        if not v.strip():
            raise ValueError('Prompt cannot be empty.')
        return v

def get_prompt_template(type: str, user_input: str) -> str:
    templates = {
        "10mark": f"Act as an academic tutor. Provide a structured 10-mark exam answer for: '{user_input}'.\nUse this structure:\n- Introduction\n- 5 Key Points with headings\n- Conclusion.",
        "20mark": f"Act as a senior professor. Provide an exhaustive 20-mark exam answer for: '{user_input}'.\nUse this structure:\n- Detailed Introduction\n- Background/Context\n- 8-10 Detailed Points\n- Illustrative Example\n- Conclusion.",
        "summarize": f"Summarize the following into crisp, exam-ready bullet points: '{user_input}'.",
        "explain": f"Explain the concept of '{user_input}' using simple analogies for a 10-year-old. Avoid jargon."
    }
    return templates.get(type, "")

@app.get("/")
async def serve_frontend():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "healthy"})

@app.post("/generate")
async def generate(request: GenerateRequest):
    if not client:
        raise HTTPException(status_code=503, detail="AI Client not initialized.")

    logger.info(f"Generating content for type: {request.type}")
    
    try:
        formatted_prompt = get_prompt_template(request.type, request.prompt)
        
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=formatted_prompt
        )
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini.")

        return {"response": response.text, "type": request.type}
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
