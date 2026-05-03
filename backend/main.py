import os
import logging
import uvicorn
from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, validator
import google.generativeai as genai
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Diagnostic: Print where we are looking for packages
import sys
logger.info(f"Python path: {sys.path[:3]}")

# --- Configuration & Security ---
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    logger.error("GEMINI_API_KEY is missing.")

app = FastAPI(
    title="AI Study Assistant API",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=5000)
    type: str = Field(..., regex="^(10mark|20mark|summarize|explain)$")

    @validator('prompt')
    def prevent_empty_prompts(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty.')
        return v

def get_prompt_template(type: str, user_input: str) -> str:
    templates = {
        "10mark": f"Act as an academic tutor. Provide a structured 10-mark exam answer for: '{user_input}'.\nUse this structure:\n- Introduction\n- 5 Key Points\n- Conclusion.",
        "20mark": f"Act as a professor. Provide an exhaustive 20-mark exam answer for: '{user_input}'.\nUse this structure:\n- Introduction\n- Background\n- 10 Detailed Points\n- Example\n- Conclusion.",
        "summarize": f"Summarize into crisp bullet points: '{user_input}'.",
        "explain": f"Explain '{user_input}' using simple analogies for a beginner."
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
    if not API_KEY:
        raise HTTPException(status_code=503, detail="API Key missing.")

    logger.info(f"Generating content for type: {request.type}")
    
    try:
        formatted_prompt = get_prompt_template(request.type, request.prompt)
        response = model.generate_content(formatted_prompt)
        return {"response": response.text, "type": request.type}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
