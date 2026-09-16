# Zippy

Zippy is a real-time voice assistant that helps a user understand their income, expenses,
loans, and credit card payments, and builds a realistic 30-day financial plan.

## Tech stack

- **Voice pipeline:** Pipecat, orchestrating Deepgram (STT), Google Gemini (LLM),
  Cartesia (TTS)
- **Real-time transport:** LiveKit
- **Backend:** FastAPI (Python)
- **Frontend:** React + TypeScript, Material UI, Zustand

## Architecture

1. User clicks "Start conversation" → backend creates a LiveKit room + tokens,
   spins up a Pipecat bot as an async task.
2. Bot and browser join the same LiveKit room — this is the audio transport.
3. Pipecat pipeline: LiveKit audio in → Deepgram STT → Gemini LLM (with tool
   calling) → Cartesia TTS → LiveKit audio out.
4. The LLM calls tools (`add_income`, `add_payment`, `flag_missing`,
   `resolve_conflict`, `mark_ready_for_planning`, etc.) that mutate a
   per-session `FinancialState` object — the single source of truth.
5. Every state mutation is diffed and pushed to the frontend over a
   WebSocket, driving live-updating cards.
6. Once enough information is gathered, a pure deterministic function
   (`planning/calculator.py`, no LLM involved) computes a day-by-day 30-day
   balance simulation and a numbered action plan.
7. The LLM narrates the computed plan back to the user — it never invents or
   calculates numbers itself.

## Setup & run

1. Clone the repo:
   ```
   git clone https://github.com/ItsAbhinavM/zippy.git
   cd zippy
   ```
2. Copy `.env.example` to `.env` inside `backend/` and fill in the keys (see
   table below).
3. Start everything with one command:
   ```
   docker compose up --build
   ```
4. Open the app at:
   ```
   http://localhost:5173
   ```

No separate terminals or manual steps are needed — the backend (FastAPI +
Pipecat) and frontend (built and served via nginx) both start from the single
`docker compose up` command.

## Environment variables

All variables are required. Set them in `backend/.env` (see `.env.example`).

| Variable | Used for | 
|---|---|
| `LIVEKIT_URL` | LiveKit server WebSocket URL |
| `LIVEKIT_API_KEY` | Signing room-access tokens |
| `LIVEKIT_API_SECRET` | Signing room-access tokens |
| `GEMINI_API_KEY` | LLM (conversation + tool calling) |
| `DEEPGRAM_API_KEY` | Speech-to-text  |
| `CARTESIA_API_KEY` | Text-to-speech |

## Project structure

```
backend/
  app/
    agent/        pipeline, tools, tool handlers, prompts
    state/        FinancialState model, mutation store, diffing
    planning/      deterministic 30-day calculator (no LLM)
    sessions/      per-session lifecycle management
    routes/        HTTP + WebSocket endpoints
  tests/           calculator, state store, tool handler tests
frontend/
  src/
    components/    voice UI (orb, captions, controls)
    components/cards/  live financial cards
    store/         Zustand state store
    livekit/       LiveKit room connection
```
