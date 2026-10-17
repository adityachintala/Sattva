# Sattva Voice Agent — Deploy Bundle

A browser voice agent that runs entirely on Sarvam: **Saaras** (speech-to-text) →
**sarvam-105b** (the reply) → **Bulbul** (the voice). English and Telugu.

This folder is everything you need. Pick one path.

---

## Run it locally (2 minutes)

```bash
pip install -r requirements.txt
export SARVAM_API_KEY=your_key_here        # Windows: set SARVAM_API_KEY=...
uvicorn server:app --reload --port 8000
```
Open <http://localhost:8000>, allow the microphone, and talk. Toggle English/తెలుగు.

If you see a brown banner saying the key is missing, the environment variable didn't reach
the server — set it and restart.

---

## Deploy to a public URL

### Option 1 — Render (easiest, has a free tier)

1. Push this folder to a **GitHub repository** (it already contains `render.yaml`).
2. Go to <https://render.com> → **New** → **Blueprint** → pick your repo.
3. Render reads `render.yaml`, builds it, and asks for one secret:
   **`SARVAM_API_KEY`** — paste your key.
4. Deploy. You get a public URL like `https://sattva-voice-agent.onrender.com`.
   Open it on your phone and talk.

> Free tier sleeps after ~15 minutes idle; the first request after that takes ~30 s to wake.
> Fine for a demo. For always-on, use the paid tier or Railway/Fly.

### Option 2 — Railway

1. New Project → **Deploy from GitHub repo**.
2. Railway detects the `Procfile` and `requirements.txt` automatically.
3. Add a variable `SARVAM_API_KEY` in Settings → Variables.
4. Deploy → **Generate Domain**.

### Option 3 — Anywhere with Docker

```bash
docker build -t sattva-voice .
docker run -p 8000:8000 -e SARVAM_API_KEY=your_key sattva-voice
```

---

## Deploy the *marketing website* (separate, instant)

The Sattva website prototype (`Sattva-Website-Prototype.html`) is a single static file — no
server needed. To get it on a public URL in about 30 seconds:

1. Go to <https://app.netlify.com/drop>
2. Drag `Sattva-Website-Prototype.html` (rename it to `index.html` first) onto the page.
3. Netlify gives you a live URL immediately. You can add a custom domain later.

(Or `vercel deploy` / GitHub Pages — same idea.)

---

## Files in this bundle

| File | Purpose |
|---|---|
| `server.py` | FastAPI server: proxies to Sarvam (STT / chat / TTS). Holds the system prompt + safety rules. |
| `index.html` | The voice-agent web page (record → Sarvam → play, EN/TE toggle). |
| `requirements.txt` | Python dependencies. |
| `Dockerfile` | Container build for any host. |
| `render.yaml` | Render blueprint (one-click deploy). |
| `Procfile` | Process definition for Railway/Heroku-style hosts. |
| `runtime.txt` | Python version pin. |

---

## Turning this into the real phone line

This web demo proves the brain. To answer **phone calls**, keep `server.py`'s three Sarvam
calls and swap the browser audio for a telephony media stream:

- **Managed:** use Sarvam Voice Agents and rent a number from Sarvam (no code).
- **Build:** use Sarvam's Pipecat/LiveKit/Twilio/Exotel integrations, keeping
  `saaras` → `sarvam-105b` → `bulbul` unchanged.

See the companion guide (`Sattva-Sarvam-Voice-Agent-Guide.md`) for both.

---

## Security notes

- The API key lives only in the server environment. Never put it in `index.html`.
- This demo has open CORS and no auth — fine for testing, but before anything public,
  add a rate limit and lock CORS to your domain.
- Patient data (names, numbers, complaints) is personal data under the DPDP Act 2023 —
  store it access-controlled, and add a "this call may be recorded" notice for phone use.
