# Backend

The backend is a modular FastAPI service responsible for:

- authentication and user session management
- emotion inference and explainability
- safety and crisis risk detection
- conversation ingestion and orchestration
- conversational memory and RAG retrieval
- emotion and safety inference pipelines
- RAG retrieval and memory integration
- analytics APIs for the dashboard

## Folder structure

- `app/api/`: versioned HTTP routes, dependencies, and endpoint grouping
- `app/core/`: configuration, security, middleware, error handling, and logging
- `app/db/`: SQLAlchemy base, async session, and persistence models
- `app/integrations/`: external integrations such as ChromaDB
- `app/repositories/`: data access layer abstractions
- `app/schemas/`: request and response contracts
- `app/services/`: business logic layer
- `tests/`: backend tests

## Why this architecture

- API routes stay thin and delegate logic to services.
- Services coordinate business rules and security without owning persistence details.
- Repositories isolate database access so storage can evolve without rewriting endpoints.
- Integrations isolate vendor-specific concerns like vector databases.
- Core utilities keep cross-cutting concerns reusable and testable.
