# Mini-SIEM Backend 🛡️

A backend security monitoring system built with **FastAPI**.  
It collects and analyzes security events, detects suspicious activity, and generates alerts.

## 🎯 Goals
- Learn backend development using FastAPI
- Understand event-driven security systems
- Build an original semester-long project

## 🧱 Tech Stack
- Python
- FastAPI
- SQLite or PostgreSQL (later)
- Git / GitHub

## 🗓️ Roadmap (Phases)
1. Project setup ✅
2. Core API design
3. Detection & alert system
4. Authentication & security
5. Stats & analytics
6. Optional extra features
7. Final documentation & presentation

---

## 🚀 Run the project
```bash
uvicorn main:app --reload
```Then open `http://127.0.0.1:8000/docs` to explore the API.

### Auth
- Write endpoints (like `POST /logs`) expect an API key header:
  - **Header**: `X-API-Key: super-secret-mini-siem-key`

### Main endpoints
- **Logs service** (`/logs`):
  - `GET /logs` – list logs
  - `GET /logs/{id}` – get single log
  - `POST /logs` – create log (triggers detection rules)
- **Alerts service** (`/alerts`):
  - `GET /alerts` – list alerts
  - `GET /alerts/{id}` – get single alert
- **Stats service** (`/stats`):
  - `GET /stats/summary` – totals, per-severity, per-source counts
  - `GET /stats/events-per-day` – events grouped by day