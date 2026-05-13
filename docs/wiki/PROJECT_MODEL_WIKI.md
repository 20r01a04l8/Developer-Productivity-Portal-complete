# Project ORM Model — Deep Dive

## Files Changed

| File | Change |
|---|---|
| `app/db/base.py` | Fixed corrupted `DateTime` line, added full documentation |
| `app/models/project.py` | Rewrote cleanly with full inline explanations |

---

## What an ORM Model Is

ORM stands for **Object-Relational Mapper**.

It is a Python class that represents a database table.
Each attribute maps to one column.
SQLAlchemy translates Python operations into SQL automatically.

```
Python code                          SQL generated
──────────────────────────────────   ──────────────────────────────────────────
db.query(Project)                 →  SELECT * FROM projects
  .filter(Project.name == "x")    →  WHERE name = 'x'
  .first()                        →  LIMIT 1
```

You never write raw SQL in the application layer.
The repository is the only layer that uses the ORM.
Routes and services never touch the DB session directly.

---

## The Full Model

```python
class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id:         Mapped[uuid.UUID]     # UUID primary key
    name:       Mapped[str]           # VARCHAR(255) NOT NULL
    owner:      Mapped[str]           # VARCHAR(255) NOT NULL
    status:     Mapped[ProjectStatus] # ENUM('active','archived','completed')
    created_at: Mapped[datetime]      # inherited from TimestampMixin
    updated_at: Mapped[datetime]      # inherited from TimestampMixin
```

---

## Why UUID Primary Key

### The problem with integer IDs

```
GET /projects/1   → works
GET /projects/2   → works
GET /projects/3   → works
```

An attacker can enumerate every project by incrementing the number.
They also know exactly how many projects exist from the highest ID they find.

### What UUID gives you

```
GET /projects/550e8400-e29b-41d4-a716-446655440000
```

- Reveals nothing about total record count
- Cannot be guessed or enumerated
- Globally unique — generated without any central counter

### UUID in distributed systems

Integer IDs require one database to own the sequence counter.
Two services cannot independently generate integer IDs without coordination.

UUID v4 is randomly generated. Two services can generate IDs at the same
millisecond on different machines and never collide.

In this project, Task Service stores `project_id` as a UUID reference.
If Project Service used integers, `project_id=1` could mean different things
across different services. UUIDs are globally unique — no ambiguity.

### `default=uuid.uuid4` vs `server_default`

```python
default=uuid.uuid4          # Python generates the UUID before INSERT
server_default=gen_random_uuid()  # PostgreSQL generates it during INSERT
```

We use `default=uuid.uuid4` (Python-side) because:
- You know the ID before the database round-trip completes
- You can return the ID in the API response immediately
- No extra DB query needed to fetch the generated ID

---

## Why Timestamps Matter

### `created_at`

Answers: "When was this record created?"

Use cases:
- Default sort order for lists ("newest first")
- Audit logs ("project was created on May 13 at 14:32")
- Data retention policies ("delete projects older than 2 years")

### `updated_at`

Answers: "When was this record last changed?"

Use cases:
- Incremental data sync: `WHERE updated_at > last_sync_time`
- Debugging: "the project was archived 3 minutes before the deployment failed"
- Optimistic locking: detect concurrent edits by comparing timestamps
- Cache invalidation: "has this record changed since I last fetched it?"

### Why `server_default=func.now()` not `default=datetime.utcnow`

```python
# Python-side default — risky
default=datetime.utcnow
# Sets the value in Python before INSERT
# Does NOT work for direct SQL inserts that bypass the ORM
# datetime.utcnow() is deprecated in Python 3.12+

# Server-side default — correct
server_default=func.now()
# Tells PostgreSQL: SET created_at = NOW() during INSERT
# Works for ORM inserts AND direct SQL inserts
# Timestamp is set by the database clock — consistent across app servers
```

### Why `DateTime(timezone=True)`

Stores as `TIMESTAMPTZ` in PostgreSQL — always UTC-aware.

Without `timezone=True`:
- Stores as `TIMESTAMP` — naive datetime, no timezone info
- If your app server is in UTC+5 and your DB server is in UTC,
  you get silent off-by-5-hours bugs that are extremely hard to debug

With `timezone=True`:
- Always stored as UTC
- Converted to the correct local time when read
- No ambiguity, no timezone bugs

---

## SQLAlchemy 2.0 Mapped[] Syntax

### Old style (SQLAlchemy 1.x)

```python
id = Column(UUID(as_uuid=True), primary_key=True)
name = Column(String(255), nullable=False)
```

Your IDE sees these as `Any`. No autocomplete. No type checking.
`project.id` could be anything — the IDE cannot help you.

### New style (SQLAlchemy 2.0)

```python
id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
name: Mapped[str] = mapped_column(String(255), nullable=False)
```

Your IDE knows:
- `project.id` is `uuid.UUID`
- `project.name` is `str`
- `project.status` is `ProjectStatus`

Type errors are caught at development time, not at runtime in production.

---

## TimestampMixin — Why a Mixin

Without the mixin, every model repeats 10 lines:

```python
class Project(Base):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Task(Base):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())  # copy-paste
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # copy-paste
```

With the mixin:

```python
class Project(TimestampMixin, Base):
    ...  # created_at and updated_at are automatically included

class Task(TimestampMixin, Base):
    ...  # same, zero duplication
```

If you need to change the timestamp strategy (e.g. add `deleted_at` for soft
deletes), you change `TimestampMixin` once and every model gets the update.

### Inheritance order matters

```python
class Project(TimestampMixin, Base):  # correct
class Project(Base, TimestampMixin):  # wrong — timestamps may not register
```

Python's MRO (Method Resolution Order) resolves left to right.
`TimestampMixin` must come before `Base` so SQLAlchemy sees the `Mapped[]`
column definitions as part of this model's table.

---

## ProjectStatus Enum

```python
class ProjectStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    completed = "completed"
```

### Why `(str, enum.Enum)` not just `enum.Enum`

```python
# Plain enum.Enum
ProjectStatus.active == "active"   # False — different types
json.dumps(ProjectStatus.active)   # TypeError — not JSON serialisable

# str + enum.Enum
ProjectStatus.active == "active"   # True — IS the string
json.dumps(ProjectStatus.active)   # "active" — works natively
```

Pydantic validates incoming JSON `"active"` directly against this enum.
SQLAlchemy stores and reads the plain string from PostgreSQL.
No custom serialiser needed anywhere.

### Why `SAEnum(ProjectStatus, name="projectstatus")`

The `name=` parameter creates a **named** PostgreSQL ENUM type:

```sql
CREATE TYPE projectstatus AS ENUM ('active', 'archived', 'completed');
```

Without `name=`, PostgreSQL creates an anonymous enum.
Anonymous enums cause problems during Alembic migrations — you cannot
reference them by name to add or remove values later.
Named enums can be altered cleanly.

---

## `__repr__` — Why It Matters

```python
def __repr__(self) -> str:
    return f"<Project id={self.id} name={self.name!r} status={self.status}>"
```

Without `__repr__`, every log line and pytest failure shows:
```
<app.models.project.Project object at 0x000001A2B3C4D5E6>
```

With `__repr__`:
```
<Project id=550e8400-e29b-41d4 name='Backend Platform' status=active>
```

This is the difference between a 30-second debug and a 30-minute debug.

---

## How a Reviewer Evaluates This File

| What they check | What they want to see |
|---|---|
| Primary key type | UUID, not integer |
| Timestamp strategy | `server_default=func.now()`, timezone-aware |
| Enum definition | `(str, enum.Enum)` with named SAEnum |
| Column typing | SQLAlchemy 2.0 `Mapped[]` syntax |
| Nullable constraints | `nullable=False` on required fields |
| Mixin usage | `TimestampMixin` — no copy-pasted timestamp columns |
| `__repr__` | Present and readable |
| Import structure | Clean, no circular imports |

---

## Interview Talking Points

**"Why did you use UUID instead of integer IDs?"**
"Integer IDs expose record counts and are enumerable — an attacker can
iterate /projects/1, /projects/2 and discover all records. UUIDs are
randomly generated, reveal nothing, and work across distributed services
without a central sequence counter. In our microservice setup, Task Service
stores project_id as a UUID reference — if we used integers, there would be
collision risk across services."

**"Explain how the ORM model works."**
"The Project class is a Python mirror of the projects table. Each Mapped[]
attribute maps to a column. When I write `db.query(Project).filter(Project.id == x)`,
SQLAlchemy generates the SQL, executes it, and returns a typed Project instance.
I never write raw SQL in the application layer — that's the repository's job."

**"Why does TimestampMixin use server_default instead of a Python default?"**
"`server_default=func.now()` tells PostgreSQL to set the timestamp at the
database level. This works even for direct SQL inserts that bypass the ORM.
It also means the timestamp is set by the database clock, not the application
clock — which matters in distributed setups where app servers might have
slight clock drift."

**"Why does the status field use (str, enum.Enum)?"**
"Because `str + enum.Enum` means the enum value IS the string. Pydantic can
validate the incoming JSON string 'active' directly against the enum without
a custom validator. SQLAlchemy stores and reads the plain string from PostgreSQL.
Without the str mixin, you'd need custom serialisers everywhere."
