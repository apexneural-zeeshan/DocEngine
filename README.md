DocEngine

DocEngine is a FastAPI backend for managing document approval workflows with role-based actions, auditability, and secure access.

Tech stack
- FastAPI for the API layer
- SQLAlchemy for data access
- JWT-based authentication
- pytest for automated testing
- Docker for containerized runs

Run locally with Docker
```bash
docker compose up --build
```
The API listens on `http://localhost:8000`.

Run tests
```bash
pytest
```

Architecture overview
DocEngine is organized around a clear separation of concerns: API routers define HTTP endpoints, services enforce workflow rules and business logic, and SQLAlchemy models map to the persistence layer. Configuration is loaded from environment variables, and shared dependencies (like DB sessions and auth helpers) are provided via FastAPI dependencies, keeping the app modular and test-friendly.
