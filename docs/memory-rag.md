# Conversational Memory and RAG System

## Architecture

Safebond uses a dual-store memory architecture:

- **PostgreSQL** stores the authoritative relational conversation history
- **ChromaDB** stores semantic memory embeddings for retrieval

```text
Message write -> PostgreSQL message row -> chunking -> embedding generation ->
ChromaDB memory index -> semantic retrieval -> reranking -> context injection
```

## Why this design

- relational storage preserves auditability and chronological history
- vector storage supports semantic recall instead of exact keyword matching
- separating storage concerns keeps the system scalable and debuggable
- personalized retrieval is enforced through `user_id` filtering before reranking

## Database schema

### `conversations`

- `id`
- `user_id`
- `title`
- `summary`
- `created_at`
- `updated_at`
- `last_message_at`

### `messages`

- `id`
- `conversation_id`
- `user_id`
- `role`
- `content`
- `created_at`

### `memory_chunks`

- `id`
- `user_id`
- `conversation_id`
- `message_id`
- `role`
- `chunk_index`
- `content`
- `token_estimate`
- `importance_score`
- `created_at`

## Embedding pipeline

- model: `sentence-transformers/all-MiniLM-L6-v2`
- normalized embeddings for cosine similarity
- lazy-loaded singleton runtime
- GPU preferred when available, CPU fallback otherwise

## Chunking strategy

- normalize whitespace
- split by sentence boundaries and line breaks
- build chunks up to a character budget
- keep a one-sentence overlap to reduce context fragmentation
- estimate importance based on first-person, emotional, and reflective cues

## Retrieval scoring

Final ranking blends:

- semantic similarity
- recency score with time decay
- importance score
- same-conversation boost

Default weights:

- semantic: `0.60`
- recency: `0.20`
- importance: `0.15`
- same-conversation boost: `0.05`

## Retrieval flow

1. User submits a query
2. Query is embedded with MiniLM
3. ChromaDB returns candidate memory chunks for that user
4. Candidates are reranked using semantic, recency, importance, and conversation continuity
5. Top memory snippets are converted into a prompt-ready injected context block

## API endpoints

- `POST /api/v1/conversations`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{conversation_id}`
- `POST /api/v1/conversations/{conversation_id}/messages`
- `GET /api/v1/conversations/{conversation_id}/messages`
- `GET /api/v1/memory/conversations/{conversation_id}/chunks`
- `POST /api/v1/memory/search`
- `POST /api/v1/rag/context`

## Context injection

The RAG service emits a structured context block intended for downstream response-generation agents. It includes:

- source role
- conversation identity
- retrieval score
- exact memory snippet

This gives the response agent continuity without dumping the entire chat history into the prompt.
