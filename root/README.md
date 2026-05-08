# CivicSight — Backend API

Civic issue reporting platform backend built with FastAPI + Supabase + Gemini/Ollama AI.

## Stack
- **API**: FastAPI (Python)
- **Database + Auth**: Supabase (PostgreSQL)
- **AI Engine**: Ollama (moondream) — swappable with Gemini/Anthropic
- **Email**: Resend
- **Hosting**: Render.com (free tier)

## Setup

### 1. Clone & create virtualenv
```bash
git clone <your-repo>
cd civic-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables
Create a `.env` file:
```env
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SUPABASE_ANON_KEY=
GEMINI_API_KEY=
RESEND_API_KEY=
```

### 3. Run locally
```bash
uvicorn main:app --reload
```

API docs available at: http://localhost:8000/docs

## Architecture

Citizen App / Staff Dashboard
↓
[ FastAPI API Layer ]
↓
┌─────────────┬──────────────┐
│ Auth        │ AI Engine    │
│ (Supabase)  │ (Ollama)     │
└─────────────┴──────────────┘
↓
[ PostgreSQL (Supabase) ]

## Modules
| Phase | Module | Status |
|-------|--------|--------|
| 1 | Database + Auth | ✅ |
| 2 | State Machine + Routing | ✅ |
| 3 | AI Engine | ✅ |
| 4 | API Layer | ✅ |
| 5 | Email Notifications | ✅ |
| 6 | Hardening | ✅ |

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /reports/ | Submit a new report |
| GET | /reports/ | List reports (role-based) |
| GET | /reports/{id} | Get single report |
| PATCH | /reports/{id}/status | Update report status |
| POST | /reports/{id}/classify | Manual AI override |
| GET | /users/me | Get current user |
| PATCH | /users/me | Update profile |
| GET | /departments/ | List departments |
| POST | /admin/promote | Promote user role |
| GET | /admin/reviews | Pending human reviews |
| POST | /admin/departments | Create department |
