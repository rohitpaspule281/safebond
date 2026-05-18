# Safebond Troubleshooting Guide

## 1. Backend dependencies fail to import

Symptoms:

- `ModuleNotFoundError: No module named 'fastapi'`
- `ModuleNotFoundError: No module named 'pydantic'`
- transformer or sentence-transformer import failures

Fix:

```bash
cd safebond/backend
pip install -r requirements.txt
```

If you prefer an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Frontend fails to start

Symptoms:

- `next: command not found`
- missing React or Next packages

Fix:

```bash
cd safebond/frontend
cp .env.local.example .env.local
npm install
npm run dev
```

## 3. PostgreSQL connection errors

Symptoms:

- `connection refused`
- `password authentication failed`
- FastAPI health check shows database unavailable

Fix:

- confirm PostgreSQL is running on port `5432`
- confirm `DATABASE_URL` matches your local instance
- if using Docker, run from `safebond/`:

```bash
docker compose up --build
```

## 4. ChromaDB or memory retrieval issues

Symptoms:

- memory search returns empty results
- vector store health shows degraded
- retrieval context never appears in chat

Fix:

- ensure `CHROMA_PERSIST_DIRECTORY` is writable
- confirm user messages are actually being sent through `/api/v1/chat/message`
- check that `MEMORY_INDEX_ASSISTANT_MESSAGES` and chunking settings are enabled in `.env`
- for a clean local reset, remove only the local `chroma/` directory if you intentionally want to rebuild the vector store

## 5. Hugging Face model download/runtime issues

Symptoms:

- first request is slow
- model load errors on first inference
- CUDA fallback warnings

Fix:

- first run may download weights and can take time
- keep `HF_LOCAL_FILES_ONLY=false` for first-time setup
- use CPU by forcing:

```env
EMOTION_DEVICE_PREFERENCE=cpu
EMBEDDING_DEVICE_PREFERENCE=cpu
SAFETY_DEVICE_PREFERENCE=cpu
```

This is often the safest local laptop configuration.

## 6. Frontend cannot reach backend

Symptoms:

- login fails with network errors
- dashboard and chat stay in loading state
- browser console shows fetch failures

Fix:

- backend should be running at `http://localhost:8000`
- frontend `.env.local` should contain:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

- backend `.env` should allow:

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 7. Safety responses always trigger

Symptoms:

- every message looks high risk
- assistant replies are always replaced by fallback

Fix:

- lower lexical sensitivity by reviewing safety rule phrases
- tune thresholds in `.env`:

```env
SAFETY_MODERATE_THRESHOLD=0.35
SAFETY_HIGH_THRESHOLD=0.58
SAFETY_CRITICAL_THRESHOLD=0.78
SAFETY_SELF_HARM_THRESHOLD=0.62
```

## 8. Analytics feel slow

Symptoms:

- dashboard takes noticeable time on first load

Fix:

- analytics currently recompute recent emotional and safety summaries from recent user messages
- this is acceptable for development, but production stabilization should cache analytics snapshots or persist derived summaries

## 9. Clean local startup checklist

1. Copy backend env:

```bash
cd safebond
cp .env.example .env
```

2. Copy frontend env:

```bash
cd frontend
cp .env.local.example .env.local
```

3. Start PostgreSQL and backend
4. Start frontend
5. Register a user
6. Send a chat message
7. Check dashboard and insights pages
