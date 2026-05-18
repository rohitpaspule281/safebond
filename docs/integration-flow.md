# Safebond Integration Flow

## Integration architecture

```text
Frontend (Next.js)
 -> Auth provider + API client
 -> FastAPI API gateway
 -> Chat orchestration service
    -> Safety evaluation
    -> Emotion detection
    -> Memory write
    -> RAG memory retrieval
    -> Draft response
    -> Response moderation
 -> PostgreSQL + ChromaDB
 -> Analytics endpoints
 -> Dashboard / chat UI
```

## Final project flow

1. User signs up or logs in from the Next.js frontend.
2. JWT is returned by FastAPI and stored in the frontend auth provider.
3. Workspace pages call authenticated backend APIs.
4. Chat requests hit the integrated `/chat/message` route.
5. Backend evaluates:
   - emotional state
   - safety risk
   - personalized memory context
6. User message is stored in PostgreSQL and indexed into ChromaDB memory.
7. RAG context is built from semantically relevant memories.
8. Assistant response is drafted and then moderated by the safety layer.
9. Final moderated assistant reply is stored and returned to the frontend.
10. Analytics pages fetch backend-computed dashboard and insight summaries.

## Request lifecycle explanation

### Authentication lifecycle

- frontend `signup` or `login` form submits credentials
- backend returns JWT + user payload
- frontend stores token locally and uses it for all protected requests
- workspace routes guard access through the auth provider

### Chat lifecycle

- frontend sends `message` and optional `conversation_id`
- backend creates or loads a conversation
- safety service scores crisis/self-harm/distress signals
- emotion service predicts primary and secondary emotions
- message is chunked, embedded, and stored in memory index
- RAG service retrieves prior relevant memory
- orchestration service drafts a context-aware supportive response
- moderation layer sanitizes or replaces the draft if needed
- final assistant message is stored and returned

### Analytics lifecycle

- frontend requests `/analytics/dashboard` or `/analytics/insights`
- backend reads recent user messages
- backend recomputes recent emotional and safety summaries
- dashboard cards, trend lines, and heatmaps are returned in frontend-ready shape

## Local startup flow

### Option 1: run manually

Backend:

```bash
cd safebond/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd safebond/frontend
cp .env.local.example .env.local
npm install
npm run dev
```

### Option 2: run with Docker Compose

```bash
cd safebond
cp .env.example .env
docker compose up --build
```

## API request examples

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "StrongPass123",
  "display_name": "Deepali",
  "timezone": "Asia/Kolkata"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "StrongPass123"
}
```

### Send integrated chat message

```http
POST /api/v1/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "conversation_id": "optional-conversation-id",
  "message": "I feel overwhelmed and my mind keeps racing at night."
}
```

### Fetch dashboard analytics

```http
GET /api/v1/analytics/dashboard
Authorization: Bearer <token>
```

### Fetch mood insights

```http
GET /api/v1/analytics/insights
Authorization: Bearer <token>
```
