# Fashion 4-Option Agent (Hackathon-ready)

This project is a hackathon-friendly full-stack app:
- Frontend: static HTML/CSS/JS served by FastAPI
- Backend: FastAPI endpoints that analyze uploaded images and call IBM Watsonx Orchestrate skills
- Orchestrate: JSON templates (skills) included for import into Watsonx Orchestrate

## Features
- Upload image → detect item type & condition (mock analyzer included)
- Four actions: Sell, Donate, Recycle, Style
- Mock mode enabled by default for quick demos (no IBM credentials required)
- Geolocation-based donate recommendations when user allows location

## Run locally (mock mode)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
export WATSONX_MOCK=true
python -m backend.main
```
Open http://localhost:10000

## To connect real Watsonx Orchestrate
1. Import JSON skill files from `/orchestrate` into Watsonx Orchestrate.
2. Set environment variables (locally or on Render):
   - WATSONX_API_KEY
   - WATSONX_ORCH_URL (override if different)
   - STYLE_SKILL_ID, RECYCLE_SKILL_ID, SELL_SKILL_ID, DONATE_SKILL_ID
   - WATSONX_MOCK=false
3. Restart backend. The backend will send payloads to your Watsonx Orchestrate endpoint for each action.

## Deploy on Render
- Use `render.yaml` included for one-click deployment (set env vars in Render dashboard).
- Render provides HTTPS automatically for your service URL.

## Notes
- The image analyzer is a simple heuristic for demo purposes. Swap `backend/image_analyzer.py` with a real model (CLIP, EfficientNet, YOLO, etc.) for better accuracy.
- Respect user privacy: images are not stored by default. Enable KEEP_UPLOADS env var only for debugging.
