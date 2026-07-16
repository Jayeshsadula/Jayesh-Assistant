# JAYESH Assistant

**A fully private, self-hosted AI assistant powered by local LLMs.**

JAYESH Assistant is a ChatGPT-like platform that runs entirely on your own
infrastructure. No OpenAI, Anthropic, or Grok API calls — all inference runs
through [Ollama](https://ollama.com) on models you control.

This project runs **natively** — no Docker required. MongoDB, ChromaDB, and
Ollama are installed and run directly on your machine.

---

## Features

- 💬 Multi-session chat with real-time token streaming (SSE)
- 🧠 Long-term memory — the assistant recalls facts and preferences across conversations
- 📄 Document intelligence (RAG) — upload PDF/DOCX/TXT and ask questions about them
- 🛠️ Tool calling — calculator, sandboxed Python execution, file search, document reader,
  folder explorer, git repository reader, sandboxed terminal
- 🔀 Multi-model support — switch between Qwen, Llama, Mistral, Gemma, and DeepSeek
- 🔐 Firebase Authentication with protected routes
- 🎨 Modern, responsive UI with dark/light mode

---

## Architecture

```
User
  │
  ▼
React Frontend (Vite + TS + Tailwind, localhost:5173)
  │  calls the backend directly over HTTP (CORS enabled)
  ▼
FastAPI Backend (localhost:8000)
  │
  ▼
AI Orchestrator (LangGraph)
  │
  ├── Memory Manager  ──▶ MongoDB + ChromaDB (semantic recall)
  ├── Tool Manager     ──▶ calculator, python exec, file/git/terminal tools
  └── RAG Engine       ──▶ ChromaDB (document chunks)
  │
  ▼
Ollama (Qwen / Llama / Mistral / Gemma / DeepSeek)
  │
  ▼
Streamed response ──▶ Frontend
```

### Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Zustand, React Router, Tailwind CSS, Framer Motion |
| Backend | FastAPI, LangGraph, LangChain, Pydantic |
| AI runtime | Ollama (Qwen, Llama, Mistral, Gemma, DeepSeek) |
| Database | MongoDB |
| Vector store | ChromaDB |
| Embeddings | `nomic-embed-text` via Ollama |
| Auth | Firebase Authentication |
| Streaming | Server-Sent Events (SSE) |

---

## Project structure

```
jayesh-assistant/
├── backend/
│   └── app/
│       ├── api/v1/endpoints/   # chat, conversations, memory, documents, models, settings, health
│       ├── agents/             # LangGraph orchestrator
│       ├── memory/             # long-term memory service
│       ├── tools/               # calculator, python exec, file/git/terminal tools + registry
│       ├── rag/                  # chunking, extraction, ChromaDB client, ingestion pipeline
│       ├── database/            # MongoDB connection + indexes
│       ├── authentication/      # Firebase token verification
│       ├── llm/                  # Ollama client wrapper
│       ├── prompts/              # system prompt construction
│       ├── streaming/            # SSE formatting
│       ├── services/             # conversation, document, settings services
│       ├── schemas/              # Pydantic models (mirrors MongoDB collections)
│       ├── config/                # centralized settings
│       ├── utils/                 # logging, exceptions
│       └── tests/                 # pytest unit tests
└── frontend/
    └── src/
        ├── components/{chat,sidebar}/
        ├── pages/                 # Login, Signup, Chat, Settings
        ├── store/                 # Zustand: auth, chat, settings
        ├── lib/                    # API client, SSE streaming, Firebase, utils
        ├── routes/                 # ProtectedRoute
        └── types/                  # shared TypeScript types
```

---

## Prerequisites

Install these on your machine:

| Component | Download | Notes |
|---|---|---|
| **Python 3.12** | https://www.python.org/downloads/ | Check "Add to PATH" during install |
| **Node.js 20** | https://nodejs.org/ | LTS version |
| **MongoDB Community Server** | https://www.mongodb.com/try/download/community | Install as a service — starts automatically on `localhost:27017` |
| **Ollama** | https://ollama.com/download | Runs automatically on `localhost:11434` after install |
| **ChromaDB** | Installed via `pip` (see below) | Run as a standalone server process |
| **Firebase project** | https://console.firebase.google.com | Free tier is enough — used for Authentication |

~16GB RAM is recommended for running 7B–9B models comfortably.

---

## Getting started

### 1. Pull your Ollama models

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```
Optionally also pull any of: `llama3.1:8b`, `mistral:7b`, `gemma2:9b`, `deepseek-r1:7b`

### 2. Start ChromaDB

In its own terminal window (leave it running):
```bash
pip install chromadb
chroma run --path ./chroma_data --port 8001
```

### 3. Set up Firebase

1. Create a project at the [Firebase Console](https://console.firebase.google.com)
2. Enable **Authentication** → Email/Password (or your preferred sign-in method)
3. Go to **Project Settings → General → Your apps** and register a web app to get
   your web config (API key, auth domain, etc.)
4. Go to **Project Settings → Service Accounts** and click "Generate new private key"
   — save the downloaded JSON file somewhere on your machine (you'll reference its
   full path in the next step)

### 4. Configure and run the backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env
```

Edit `backend/.env`:
- `JWT_SECRET_KEY` — any long random string
- `FIREBASE_PROJECT_ID` — your Firebase project ID
- `FIREBASE_CREDENTIALS_PATH` — the **full absolute path** to the service account
  JSON you downloaded in step 3 (e.g. `C:\Users\you\path\to\firebase-service-account.json`)

Then start it:
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Configure and run the frontend

In a new terminal:
```bash
cd frontend
npm install
cp .env.example .env
```

Edit `frontend/.env` and fill in the `VITE_FIREBASE_*` values from step 3's web
app config. `VITE_API_BASE_URL` should already be correct
(`http://localhost:8000/api/v1`).

Then start it:
```bash
npm run dev
```

### 6. Open the app

Visit **http://localhost:5173**

---

## What's running

You'll have 3 terminal windows open:
1. `chroma run` (ChromaDB, port 8001)
2. `uvicorn app.main:app` (backend, port 8000)
3. `npm run dev` (frontend, port 5173)

MongoDB and Ollama run silently as background services — no terminal window needed
for either.

---

## Running tests

```bash
cd backend
pip install -r requirements.txt --break-system-packages
python3 -m pytest app/tests/ -v
```

---

## API overview

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/chat` | Non-streaming chat completion |
| POST | `/api/v1/chat/stream` | Streaming chat completion (SSE) |
| GET/POST | `/api/v1/conversations` | List / create conversations |
| PATCH/DELETE | `/api/v1/conversations/{id}` | Rename / delete a conversation |
| GET | `/api/v1/conversations/{id}/messages` | Get a conversation's messages |
| GET/POST | `/api/v1/memory` | List / add long-term memories |
| DELETE | `/api/v1/memory/{id}` | Delete a memory |
| POST | `/api/v1/upload` | Upload a document for RAG |
| GET/DELETE | `/api/v1/documents` | List / delete uploaded documents |
| GET | `/api/v1/models` | List configured & available Ollama models |
| GET/PUT | `/api/v1/settings` | Get / update user settings |

Full interactive docs are available at **http://localhost:8000/docs** while the
backend is running.

---

## Security notes

- All chat/memory/document/settings endpoints require a valid Firebase ID
  token (`Authorization: Bearer <token>`), verified server-side.
- The Python execution and terminal tools run in restricted subprocesses
  with a strict allow-list, timeouts, and no shell metacharacters — they
  cannot install packages, access the network, or escape the sandboxed
  upload directory.
- Rate limiting is applied per-IP via `slowapi`.
- No secrets are hardcoded; everything is sourced from environment variables.
- Never commit your `.env` files or your Firebase service account JSON.

---

## Troubleshooting

**"Could not reach Ollama"** — make sure `ollama` is running (`ollama list` should
work in a terminal) and that `OLLAMA_BASE_URL` in `backend/.env` matches where it's
listening (default `http://localhost:11434`).

**"Could not reach the vector store"** — make sure the `chroma run` process is
still running in its terminal window.

**MongoDB connection errors** — check that the MongoDB service is running:
on Windows, look for "MongoDB Server" in `services.msc`.

**Firebase `FileNotFoundError`** — double check `FIREBASE_CREDENTIALS_PATH` in
`backend/.env` is an absolute path to a file that actually exists, not a relative
path or a leftover placeholder value.

---

## License

This project is provided as-is for self-hosted, private use.
#   J a y e s h - A s s i s t a n t  
 