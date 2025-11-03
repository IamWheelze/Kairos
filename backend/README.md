Kairos Backend

Voice-activated media control for ProPresenter with HITL and Data Portal.

Features
- ProPresenter control (Next/Prev/Clear/GoToSong, plus section/media stubs)
- HITL dashboard (live log, pending confirm/cancel, AI toggle, record-to-STT)
- Data Portal (song mappings + Dialogflow SongName entity sync)
- NLU: Rule-based default; Dialogflow CX when configured
- STT: Google Cloud Speech (upload or browser recording)
- Music ID: ACRCloud (audio upload) mapped to GoToSong
- Health endpoints, env loading, basic tests

Setup
- Python 3.11 recommended
- Install: `pip install -r backend/requirements.txt`
- Configure `backend/.env` (copy from `.env.example`)
  - ProPresenter: `PROP_HOST`, `PROP_PORT`, `PROP_PASSWORD`
  - Dialogflow: `GOOGLE_APPLICATION_CREDENTIALS`, `DIALOGFLOW_PROJECT_ID`, `DIALOGFLOW_LOCATION`, `DIALOGFLOW_AGENT_ID`
  - ACRCloud: `ACRCLOUD_HOST`, `ACRCLOUD_KEY`, `ACRCLOUD_SECRET`
- Run dev server:
  - PowerShell: `./scripts/run_dev.ps1`
  - CMD: `scripts\run_dev.bat`
- Open:
  - HITL: http://localhost:8000/hitl
  - Portal: http://localhost:8000/portal

Docker
- Build: `docker build -t kairos .`
- Run: `docker run -p 8000:8000 --env-file backend/.env kairos`

Tests
- `pytest -q`

