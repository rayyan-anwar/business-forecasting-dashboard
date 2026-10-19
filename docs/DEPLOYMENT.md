# Deployment

Author: Rayyan Anwar

## Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/evaluate.py          # about a minute
uvicorn app.main:app --port 8020    # http://127.0.0.1:8020 -> "Use sample sales data"
```
## Docker
`docker compose up --build` (port 8020, health `/health`). Written but **not built or run** in the authoring sandbox; CI has a `docker build` job.
## Cloud
Any container host: build and push (your account), expose 8020 behind HTTPS, probe `/health`. Stateless, no database or secrets. Uploads are capped at 5 MB / 300,000 rows / 20 series; a 20-series daily upload takes about 10 s of CPU, so set request timeouts of at least 60 s and consider a job queue for heavier use. The API has no authentication: because uploaded business data can be sensitive, restrict access (VPN, IAP, auth proxy) before real use. Not deployed by the author.
## Screenshots
Click "Use sample sales data", pick a product and capture the forecast chart and "Why this model?" panel into `docs/screenshots/` (none bundled).
