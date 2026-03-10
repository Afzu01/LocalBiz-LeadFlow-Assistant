# LocalBiz LeadFlow Assistant

A practical lead management backend for small businesses receiving WhatsApp and web inquiries.

## Portfolio pitch

A lightweight CRM-intelligence layer that converts inbound messages into prioritized, actionable sales tasks.

## Why this helps real users

- Captures leads instantly from webhook events
- Classifies lead intent (pricing, booking, support, general)
- Scores urgency so teams focus on high-value leads first
- Tracks follow-up status to reduce lost opportunities

## Features

- Webhook endpoint for incoming lead events
- Intent detection and lead scoring
- Follow-up status updates
- Summary dashboard and modern `/ui`

## Architecture

- FastAPI API with webhook-first ingestion flow
- Rule-based intent and lead score generation
- SQLite persistence for lead lifecycle tracking
- Frontend dashboard for triage and status management

## Run

```powershell
cd D:\Code\python\localbiz-leadflow-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8101
```

- UI: http://127.0.0.1:8101/ui
- Docs: http://127.0.0.1:8101/docs

## API quick test

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8101/webhooks/lead" -ContentType "application/json" -Body '{"name":"Aarav","message":"Need booking this weekend","source":"whatsapp"}'
```

## Recruiter demo points

1. Send simulated lead webhook from UI
2. Explain auto intent + score generation
3. Update status from `new` to `qualified`
4. Show how this prevents missed follow-ups

## Screenshots / Demo GIF

- Add dashboard screenshot (lead table + status columns)
- Optional: add short GIF showing webhook ingest to qualified status
