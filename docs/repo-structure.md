# Repo Structure Notes

## Design goals

- keep AI experimentation separate from production APIs
- make the backend independently deployable
- support research artifacts, evaluation, and demos
- keep room for future mobile or voice clients

## Folder intent

- `backend/`: API server, orchestration, services, storage integrations, tests
- `frontend/`: dashboard and chat UI
- `ai/`: prompt specs, notebooks, model settings, evaluation assets
- `data/knowledge_base/`: curated wellness documents for RAG ingestion
- `data/evaluation/`: benchmark prompts, expected labels, and offline test data
- `infra/`: containerization and deployment files
- `docs/`: architecture and academic documentation
- `scripts/`: setup, ingestion, export, and maintenance helpers
