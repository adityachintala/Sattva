"""
Sattva voice agent — Sarvam-only web demo.

Runs a browser voice agent end to end on Sarvam:
  record -> Saaras (STT) -> sarvam-105b (LLM) -> Bulbul (TTS) -> play

Setup:
  pip install fastapi uvicorn requests python-multipart
  export SARVAM_API_KEY=your_key_here
  uvicorn server:app --reload --port 8000
Then open http://localhost:8000 and allow the microphone.

The API key stays on the server. Never put it in the browser.
"""
import os
import requests
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

SARVAM_KEY = os.environ.get("SARVAM_API_KEY", "")
BASE = "https://api.sarvam.ai"
HEADERS = {"api-subscription-key": SARVAM_KEY}

app = FastAPI(title="Sattva Sarvam voice agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SYSTEM = """You are the phone receptionist for Sattva Wellness Centre, a nature cure,
yoga and Ayurveda retreat in Shivalingapur village, Chennur mandal, Mancherial district,
Telangana. Contact: +91 93468 67079 and +91 96522 27097. Consultation hours 9am-12pm and
2pm-4pm. Doctors: Dr. K. N. Sukumar and Dr. P. Sameera Reddy (Nature Cure & Yoga), and
Dr. Samatha Potu (Ayurveda). Rooms: Dormitory, Special (twin), A/C Special (twin); rates
from about Rs 1200 per night. Programmes: 7-day Detox, 14-day Panchakarma, Yoga Teacher
Training. Campus: 20 acres, fruit orchard, yoga halls, goshala with 120+ native cows.

RULES:
- Answer in 1-3 short sentences. Warm, calm, respectful. This is spoken aloud: no lists,
  no markdown, no emojis.
- Match the caller's language: reply in Telugu if they speak Telugu, English if English.
- Never diagnose, never promise a cure, never quote a final price. Offer a callback.
- If the caller wants a human, or you don't know the answer, reply with exactly the token
  [CALLBACK] and nothing else.
- If the caller describes a medical emergency (chest pain, bleeding, unconscious, can't
  breathe, stroke), reply with exactly the token [EMERGENCY] and nothing else."""


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()


@app.post("/api/stt")
async def stt(file: UploadFile = File(...), lang: str = Form("unknown")):
    """Speech -> text via Saaras."""
    audio = await file.read()
    r = requests.post(
        f"{BASE}/speech-to-text",
        headers=HEADERS,
        files={"file": (file.filename or "audio.webm", audio, file.content_type or "audio/webm")},
        data={"model": "saaras:v3", "mode": "transcribe", "language_code": lang},
        timeout=60,
    )
    if r.status_code != 200:
        return JSONResponse({"error": r.text}, status_code=r.status_code)
    return {"transcript": r.json().get("transcript", "")}


@app.post("/api/chat")
async def chat(req: Request):
    """Conversation via sarvam-105b."""
    body = await req.json()
    messages = [{"role": "system", "content": SYSTEM}] + body.get("messages", [])
    r = requests.post(
        f"{BASE}/v1/chat/completions",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"model": "sarvam-105b", "messages": messages, "temperature": 0.4},
        timeout=60,
    )
    if r.status_code != 200:
        return JSONResponse({"error": r.text}, status_code=r.status_code)
    reply = (r.json()["choices"][0]["message"]["content"] or "").strip()
    return {"reply": reply}


@app.post("/api/tts")
async def tts(req: Request):
    """Text -> speech via Bulbul. Returns base64 WAV."""
    body = await req.json()
    lang = body.get("lang", "en-IN")
    speaker = {"te-IN": "neha", "en-IN": "ishita"}.get(lang, "ishita")
    r = requests.post(
        f"{BASE}/text-to-speech",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "text": body["text"],
            "language_code": lang,
            "speaker": speaker,
            "model": "bulbul:v3",
            "speech_sample_rate": 22050,
        },
        timeout=60,
    )
    if r.status_code != 200:
        return JSONResponse({"error": r.text}, status_code=r.status_code)
    audios = r.json().get("audios", [])
    return {"audio_base64": audios[0] if audios else ""}


@app.get("/api/health")
def health():
    return {"ok": True, "key_configured": bool(SARVAM_KEY)}
