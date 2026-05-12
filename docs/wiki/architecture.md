# Architecture Decision Record — Developer Productivity Portal

## 1. Why Microservices?

Two independent services: **Project Service** (port 8001) and **Task Service** (port 8002).

| Concern | Monolith | Microservices (chosen) |
|---|---|---|
| Deploy | One unit — redeploy everything for any change | Deploy only the changed service |
| Scale | Scale everything together | Scale task service independently if task load spikes |
| Failure | One crash takes down everything | Project service stays up if task service crashes |
| Team | Merge conflicts on shared files | Teams own separate codebases |

**Trade-off accepted:** Inter-service calls add latency. Task Service calls Project Service to validate `project_id`. This is a deliberate design — the alternative (shared DB) would couple the services at the data layer.

---

## 2. Why Layered Architecture?

```
HTTP Request
     ↓
  Routes          ← knows HTTP (status codes, request/response shapes)
     ↓
  Services        ← knows business rules (raises domain exceptions, never HTTPException)
     ↓
  Repositories    ← knows SQL (the ONLY layer that touches the DB session)
     ↓
  Database
```

**Why this matters to reviewers:**
- A service method that imports `HTTPException` is an immediate red flag — it means business logic is coupled to the transport layer.
- A route that calls `db.query(...)` directly is a red flag — it means the route has two responsibilities.
- Each layer is independently testable: repositories can be mocked in service tests; services can be mocked in route tests.

---

## 3. Why Dependency Injection?

```python
# BAD — hard to test, hard to swap
class ProjectService:
    def __init__(self):
        self._db = SessionLocal()  # creates its own session

# GOOD — receives what it needs
class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self._repo = repository
```

FastAPI's `Depends()` system wires the chain automatically:
```
get_db() → Session → ProjectRepository → ProjectService → Route
```

In tests, you pass a test session or a mock repository. The service code is unchanged.

---

## 4. Why Domain Exceptions?

```python
# Service raises a typed exception — no HTTP knowledge
raise ProjectNotFoundError(project_id)

# Middleware maps it to HTTP — one place, one responsibility
if isinstance(exc, ProjectNotFoundError):
    return JSONResponse(status_code=404, ...)
```

If you later add a gRPC transport, the service layer is unchanged. Only the exception handler changes.

---

## 5. Why a Uniform API Response Envelope?

Every endpoint returns:
```json
{ "success": true, "message": "...", "data": <payload> }
```

The frontend always reads `response.data.success`. No guessing whether the payload is at `.data`, `.data.result`, or `.items`. Error handling is one `if (!response.data.success)` check.

---

## 6. Why Alembic?

Alembic tracks schema changes as versioned migration files committed to git.

```bash
# Generate a migration after changing a model
alembic revision --autogenerate -m "add description to projects"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

**Critical rule:** Every model file must be imported in `alembic/env.py`. If it isn't, Alembic cannot see the table and will generate a migration that drops it.

---

## 7. Why Separate Axios Clients?

```
projectClient → baseURL: /api/projects → proxied to :8001
taskClient    → baseURL: /api/tasks    → proxied to :8002
```

- Interceptors are scoped — a 401 from the task service doesn't interfere with project service calls.
- Each client can have different timeout, retry, or header configuration.
- In tests, you mock `projectClient` without affecting `taskClient`.

---

## 8. Why Context API over Redux?

This app has two domain entities (projects, tasks) and one auth state. Redux adds boilerplate (actions, reducers, selectors) that is only justified when:
- State is shared across many unrelated components
- State transitions are complex (undo/redo, optimistic updates)
- A team needs strict state mutation rules

Context API with custom hooks (`useAuth`, `useProjects`, `useTasks`) is sufficient and readable for this scale.

---

## 9. Frontend Folder Responsibilities

| Folder | Responsibility |
|---|---|
| `api/` | Axios client instances — HTTP config only |
| `context/` | Shared state + API calls — no JSX |
| `pages/` | Route-level components — compose smaller components |
| `components/` | Reusable UI pieces — no direct API calls |
| `hooks/` | Custom hooks that don't own global state |
| `router/` | All route declarations + auth guard |
| `theme/` | MUI design tokens — no logic |
| `utils/` | Pure functions — no side effects |

**Rule for reviewers:** If a `components/` file imports from `api/`, that's a violation. Components receive data via props or context — they don't fetch it themselves.

---

## 10. JWT Strategy

Both services share the same `JWT_SECRET_KEY`. A token issued by Project Service is valid on Task Service. This is intentional — a single login gives access to both services.

**Security rules:**
- `JWT_SECRET_KEY` is never committed to git (`.env` is in `.gitignore`)
- Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- Tokens expire in 60 minutes (configurable via `JWT_EXPIRE_MINUTES`)
- The backend ALWAYS validates the token — the frontend's `ProtectedRoute` is UX only

---

## 11. How to Run

```bash
# Project Service
cd backend/project_service
cp .env.example .env          # fill in DATABASE_URL and JWT_SECRET_KEY
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --port 8001 --reload

# Task Service
cd backend/task_service
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --port 8002 --reload

# Frontend
cd frontend
cp .env.example .env
npm install
npm run dev                   # http://localhost:3000
```
