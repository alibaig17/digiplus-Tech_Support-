# 🚀 AI Support Copilot

An AI-powered service desk. Support engineers create tickets (with optional
screenshots), get automatic AI triage (summary, category, priority, root
cause, impact/urgency/complexity scores), chat with a ticket-grounded AI
assistant, search past incidents semantically, catch duplicates on creation,
maintain a knowledge base, and track everything on an analytics dashboard.

Built for the **DigiPlus AI-Powered Service Desk** technical assessment, and
extended per the fuller "AI Support Copilot" spec (Email OTP auth, roles,
ChromaDB vector search, OCR, knowledge base, analytics).

---

## 🧱 Tech stack

| Layer            | Choice |
|-------------------|--------|
| Frontend          | React 18 + Vite + TailwindCSS + React Router + Axios + Recharts |
| Backend           | FastAPI (Python 3.12) |
| Database          | **MongoDB Atlas** (via Motor, async driver) |
| Auth              | Email OTP (sent via **Brevo**) → JWT |
| AI                | **Gemini 2.5 Flash** (`google-generativeai`) — analysis, chat, resolution drafting, embeddings |
| Vector search      | **ChromaDB** (persistent local store) — similar/duplicate incident detection & semantic search |
| OCR               | **EasyOCR** — reads text out of uploaded error screenshots |
| Storage           | Local `uploads/` folder |
| Seed data         | [`mindweave/help-desk-tickets`](https://huggingface.co/datasets/mindweave/help-desk-tickets) via the HuggingFace `datasets` library |

---

## 📁 Project structure

```
ai-support-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, routers, CORS, static /uploads
│   │   ├── config.py             # env-driven settings
│   │   ├── database.py           # MongoDB collections + indexes
│   │   ├── auth/dependencies.py  # JWT auth guards (get_current_user, require_admin)
│   │   ├── models/schemas.py     # Pydantic request/response models
│   │   ├── routers/              # auth, tickets, assistant, search, knowledge_base, analytics, users
│   │   ├── services/             # brevo_service, gemini_service, ocr_service, vector_service
│   │   └── utils/security.py     # JWT + OTP helpers
│   ├── seed/
│   │   ├── seed_users.py         # sample admin/engineer users
│   │   └── seed_tickets.py       # loads mindweave/help-desk-tickets from HuggingFace
│   ├── uploads/                  # uploaded screenshots (served at /uploads/*)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                # Login, Dashboard, Tickets, TicketDetails, KnowledgeBase, Search, Analytics, Profile
│   │   ├── components/           # Layout, Badges
│   │   ├── context/AuthContext.jsx
│   │   └── api/client.js         # Axios client + all API calls
│   ├── package.json, vite.config.js, tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Setup

### 1. Prerequisites

- Node.js 20+ and npm
- Python 3.12
- A **MongoDB Atlas** cluster (free tier is fine) — [mongodb.com/atlas](https://www.mongodb.com/atlas)
- A **Brevo** account for OTP emails — [app.brevo.com](https://app.brevo.com) (free tier: 300 emails/day)
- A **Gemini API key** — [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

> 💡 **No API keys yet?** The app still runs. With `DEV_MODE_LOG_OTP=true`
> (default), OTP codes print to the backend console instead of emailing.
> Without a `GEMINI_API_KEY`, AI features return a friendly "not configured"
> message instead of crashing, so you can explore the whole app before
> wiring up billing.

### 2. MongoDB Atlas

1. Create a free cluster.
2. Create a database user + password.
3. Network Access → allow your IP (or `0.0.0.0/0` for local dev).
4. Copy the connection string (`mongodb+srv://...`).
5. Users are **not** self-registered. Add at least one user manually, either:
   - via MongoDB Atlas UI, insert into the `users` collection:
     ```json
     { "name": "Ali Baig", "email": "ali@gmail.com", "role": "admin", "createdAt": { "$date": "2026-01-01T00:00:00Z" } }
     ```
   - or run the seed script (`seed_users.py`, see step 5) which creates 3 sample users.

### 3. Brevo (Email OTP)

1. Sign up at [brevo.com](https://www.brevo.com).
2. Settings → SMTP & API → API Keys → create a new key.
3. Verify a sender email/domain (Brevo requires this to send).
4. Put the key in `backend/.env` as `BREVO_API_KEY`, and set `DEV_MODE_LOG_OTP=false` to actually send emails.

### 4. Gemini AI

1. Get a key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
2. Put it in `backend/.env` as `GEMINI_API_KEY`.
3. Model used: `gemini-2.5-flash` (configurable via `GEMINI_MODEL`).

### 5. Backend

```bash
cd backend
cp .env.example .env
# edit .env: MONGODB_URI, BREVO_API_KEY, GEMINI_API_KEY, JWT_SECRET, etc.

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Seed sample users (creates ali@gmail.com as admin, plus 2 engineers)
python -m seed.seed_users

# Seed ~150 sample tickets from the HuggingFace help-desk-tickets dataset
python -m seed.seed_tickets --limit 150
# (add --with-embeddings to also index them into ChromaDB — requires GEMINI_API_KEY, slower)

# Run the API
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 6. Frontend

```bash
cd frontend
cp .env.example .env      # VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

App: `http://localhost:5173`

Log in with any seeded email (e.g. `ali@gmail.com`). If `DEV_MODE_LOG_OTP=true`,
watch the **backend terminal** for the printed OTP code.

### 7. Docker (optional)

Uses MongoDB Atlas (cloud) — no local Mongo container.

```bash
# fill in backend/.env first (see step 5)
docker compose up --build
```

- Backend → `http://localhost:8000`
- Frontend → `http://localhost:5173`

---

## 🔌 API endpoints

```
POST   /auth/send-otp
POST   /auth/verify-otp
GET    /me

POST   /tickets                    (multipart: title, description, reporter_name,
                                     reporter_email, category, priority, screenshot?)
GET    /tickets
GET    /tickets/{id}
PUT    /tickets/{id}
DELETE /tickets/{id}
POST   /tickets/{id}/analyze        # re-run AI triage
GET    /tickets/{id}/assistant      # chat history
POST   /tickets/{id}/assistant      # ask AI assistant
POST   /tickets/{id}/resolve        # no body -> AI drafts; with body -> saves & resolves
GET    /tickets/{id}/resolution

GET    /search?q=...

GET    /kb        POST /kb        PUT /kb/{id}        DELETE /kb/{id}

GET    /analytics/overview

GET    /users (admin)   POST /users (admin)   DELETE /users/{id} (admin)
```

---

## 🧠 How the AI is used (not hard-coded rules)

- **Ticket analysis**: Gemini generates summary, category, priority, root
  cause, suggested resolution, and impact/urgency/complexity scores from the
  ticket text (+ OCR'd screenshot text if present).
- **Screenshot → OCR → AI**: EasyOCR extracts text from the uploaded image;
  that text is fed into the same Gemini analysis prompt.
- **Duplicate/similar incident detection**: every ticket's title+description
  is embedded (`text-embedding-004`) and stored in ChromaDB; on creation, a
  nearest-neighbor query surfaces similar past tickets and their resolutions.
- **AI Assistant chat**: grounded in the ticket, top similar incidents, and
  matching knowledge-base articles — not a generic chatbot.
- **Resolution generator**: Gemini drafts root cause / actions taken /
  summary / outcome from the ticket + full chat transcript; the engineer can
  edit before saving.
- **Search**: combines ChromaDB semantic similarity with MongoDB full-text
  search so results are meaningful even before/without embeddings.

---

## 🗃️ Seed data note (HuggingFace dataset)

`mindweave/help-desk-tickets` ships as a multi-table dataset (`agents`,
`categories`, `comments`, `tickets`, `sla_breaches`). `seed_tickets.py` pulls
the `tickets` subset via the `datasets` library, and **normalizes flexible
column names** (`subject`/`title`, `description`/`body`, `priority`/`P1..P4`,
etc.) into our schema, since exact column names can vary between the free
sample and full dataset. If the dataset can't be downloaded (offline / no HF
access), the script falls back to a small built-in sample so the app is still
fully demoable.

---

## ⚠️ Assumptions & known limitations

- **No public registration** by design — matches the spec ("Users are added
  manually"). Admins add users via `/users` (Profile page) or directly in Atlas.
- **EasyOCR** downloads its model weights on first run and is CPU-bound —
  the first screenshot analysis will be noticeably slower.
- **ChromaDB is local/file-based** (`chroma_data/`), not a managed service —
  fine for an assessment/demo; swap for a hosted vector DB in production.
- Without a `GEMINI_API_KEY`, AI endpoints return a placeholder message
  rather than failing, so the rest of the app (CRUD, auth, KB, analytics)
  remains fully testable.
- Embeddings are only generated when Gemini is configured — search still
  works via MongoDB text search as a fallback, just without the % similarity
  score if the ticket vector wasn't embedded.
- `JWT_SECRET` in `.env.example` is a placeholder — replace with a long
  random string in any real deployment.

---

## 🧪 Quick smoke test

1. `python -m seed.seed_users && python -m seed.seed_tickets --limit 50`
2. Start backend + frontend.
3. Log in as `ali@gmail.com` → watch backend console for OTP.
4. Dashboard should show ~50 seeded tickets across statuses.
5. Create a new ticket describing "Outlook keeps asking for MFA" → AI
   analysis + similar-incident warning should appear (if `GEMINI_API_KEY`
   is set and `--with-embeddings` was used during seeding, or after a few
   tickets have been created live, since creation always embeds).
6. Open a ticket → ask the AI Assistant a question → see a grounded reply.
7. Resolve the ticket → check Analytics dashboard updates.
