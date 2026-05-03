import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the same directory as this file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    # Using gemini-flash-latest for best compatibility
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    print("Warning: GEMINI_API_KEY not found.")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the 'static' directory
# This will be used in production to serve the React build
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerateRequest(BaseModel):
    prompt: str
    type: str  # '10mark', '20mark', 'summarize', 'explain'

@app.get("/")
async def root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Study Assistant API is running. Build the frontend to see the UI."}

@app.post("/generate")
async def generate_content(request: GenerateRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured on server.")

    # Properly construct prompt based on type
    if request.type == "10mark":
        final_prompt = f"Act as an academic expert. Generate a structured 10-mark exam answer for: \"{request.prompt}\"\n\nFormat:\n- Introduction\n- Key Points (bullets or short paragraphs)\n- Conclusion"
    elif request.type == "20mark":
        final_prompt = f"Act as an academic expert. Generate a comprehensive 20-mark exam answer for: \"{request.prompt}\"\n\nFormat:\n- Detailed Introduction\n- Headings + Subpoints\n- Examples (if applicable)\n- Conclusion"
    elif request.type == "summarize":
        final_prompt = f"Summarize the following notes into crisp, exam-focused bullet points:\n\"{request.prompt}\"\n\nFormat:\n- Bullet points only"
    elif request.type == "explain":
        final_prompt = f"Explain this concept in very easy language, like I'm 10 years old:\n\"{request.prompt}\"\n\nFormat:\n- Simple language\n- Use examples\n- Avoid jargon"
    else:
        raise HTTPException(status_code=400, detail="Invalid prompt type.")

    try:
        # Ensure final_prompt is a string
        response = model.generate_content(final_prompt)
        return {"response": response.text}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
