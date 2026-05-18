# Safebond Backend Foundation

## Phase 1 scope

This document captures the production-grade backend foundation for Safebond before AI feature modules are added.

## Folder-by-folder explanation

### `backend/app/api/`

- holds versioned route definitions
- keeps HTTP concerns separate from business logic
- includes shared dependencies such as current-user resolution

### `backend/app/core/`

- centralizes configuration, logging, JWT utilities, middleware, and error handling
- keeps cross-cutting concerns reusable across modules

### `backend/app/db/`

- owns SQLAlchemy base classes, async engine, session lifecycle, and relational models
- makes PostgreSQL integration explicit and scalable

### `backend/app/integrations/`

- encapsulates external systems like ChromaDB
- avoids scattering vendor-specific code across the codebase

### `backend/app/repositories/`

- provides persistence operations behind small interfaces
- keeps service code focused on domain logic instead of SQL details

### `backend/app/services/`

- contains use-case logic such as authentication and readiness evaluation
- becomes the main home for future orchestration logic

### `backend/app/schemas/`

- defines stable API contracts
- separates validation and serialization from ORM models

### `backend/tests/`

- isolates backend verification
- prepares the repo for CI and regression testing

## Architectural decisions

### Why FastAPI

- async-ready, strong typing, automatic OpenAPI docs, and excellent fit for ML-serving backends

### Why async SQLAlchemy

- scales better for API workloads and future background tasks than a tightly coupled synchronous ORM stack

### Why JWT for Phase 1

- simple, stateless, deployable across Render or containerized environments, and easy to explain in viva settings

### Why ChromaDB abstraction

- allows local persistent vector storage now and future swap-out to remote vector services later

### Why structured logging

- makes debugging and deployment observability much stronger than print-style logging

### Why middleware-driven request IDs

- request tracing becomes possible immediately, which is especially useful when multi-agent orchestration is added later
