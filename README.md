# AI Study Assistant 🎓✨

An expert full-stack web application designed to help students master complex concepts and prepare for exams using **Google Gemini 1.5 Flash**.

## 🌟 Key Features

- **Expert Generation**: Specialized prompts for 10-mark and 20-mark exam-ready answers.
- **Concept Simplification**: "Explain Simply" mode uses analogies and clear language for beginners.
- **Crisp Summarization**: Convert long notes into bullet points focused on exam recall.
- **Accessible UI**: Fully ARIA-compliant frontend with high-contrast theme and responsive design.

## 🛠️ Tech Stack & Architecture

- **AI Engine**: [Google Gemini 1.5 Flash](https://ai.google.dev/models/gemini)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Frontend**: [React](https://reactjs.org/) (Vite)
- **Deployment**: [Google Cloud Run](https://cloud.google.com/run) (Dockerized)

## 🛡️ Security & Quality

- **Input Validation**: Robust Pydantic models prevent prompt injection and resource abuse (min/max length checks).
- **CORS Handling**: Configured for secure cross-origin resource sharing.
- **Logging**: Comprehensive backend logging for auditability and rapid debugging.
- **Type Safety**: Fully typed Python backend and structured React component architecture.
- **Accessibility**: Semantic HTML and ARIA labels ensure the tool is usable by everyone.

## 🚀 Getting Started

### 1. Environment Setup
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_google_api_key_here
```

### 2. Local Development
**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 3. Running Tests
```bash
cd backend
pytest test_main.py
```

## ☁️ Deployment

The project is optimized for **Google Cloud Run** using a unified multi-stage `Dockerfile`.

```bash
# Build & Push
gcloud builds submit --tag gcr.io/[PROJECT_ID]/ai-study-assistant

# Deploy
gcloud run deploy ai-study-assistant \
  --image gcr.io/[PROJECT_ID]/ai-study-assistant \
  --set-env-vars GEMINI_API_KEY=your_key
```

---
*Built with ❤️ for students using Google AI.*
