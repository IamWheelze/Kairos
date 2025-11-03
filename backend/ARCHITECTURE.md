Kairos Backend Architecture

Overview
- FastAPI app exposes:
  - HITL UI (WebSocket events, operator controls)
  - Data Portal (song mappings + Dialogflow entity sync)
  - API endpoints for intents, NLU, STT, Music ID, health, and state
- Orchestrator executes intents via ProPresenter client with HITL confirmation flow.
- Integrations are behind interfaces: NLU (rule-based or Dialogflow CX), STT (Google), Music ID (ACRCloud).

Key Paths
- Voice: Browser MediaRecorder → `/api/stt/recognize` → Google STT → NLU → Orchestrator → ProPresenter
- Text: HITL form → `/api/nlu/detect` → NLU → Orchestrator → ProPresenter
- Music: Audio upload → `/api/music/identify` → ACRCloud → Orchestrator (GoToSong)
- Portal: Add song mapping → optional DF CX entity sync

HITL
- WebSocket `/ws/hitl` receives events and allows confirm/cancel of low-confidence intents.
- Toggle AI enable/disable via `/api/state`.

Health
- `/healthz` basic service info; `/readyz` readiness (ProPresenter connected).

Configuration
- `.env` or environment vars (see `.env.example`). Use `scripts/run_dev` to load `.env` and run server.

