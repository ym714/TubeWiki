# Technical Specification: FlashNote AI

## Critique Summary (Red Team Review - Round 4)
We performed a final "Robustness & Reliability" review.
*   **Idempotency**: Since QStash guarantees "At Least Once" delivery, the Worker **MUST** be idempotent. We added a check to skip processing if the Note is already `COMPLETED`.
*   **Retry Policy**: Explicitly defined the QStash retry configuration (Max Retries = 3, Exponential Backoff) to handle transient failures without overwhelming the Worker.
*   **Local Development**: Clarified the use of `ngrok` or a local QStash emulator for testing Webhooks.

## What we did
We designed a **Serverless, Event-Driven Architecture** for FlashNote AI. The system is composed of two distinct services: a **Core Service** (User API) and a **Worker Service** (AI Processing), decoupled by **Upstash QStash**. This architecture allows the system to handle long-running video processing tasks (up to 1 hour) asynchronously without blocking the user experience, while incurring **zero infrastructure costs** when idle.

## Development Guidelines
### Core Principles
1.  **Strict Separation of Concerns**:
    *   **Core**: "The Manager". Handles User Auth, Database State, and Job Dispatching. It never performs heavy computation.
    *   **Worker**: "The Specialist". A private API that performs AI tasks. It is stateless and triggered *only* via Webhook from the Event Bus.
2.  **Serverless & Managed**:
    *   **Database**: **Supabase** (PostgreSQL + Auth). **CRITICAL**: Must use Transaction Pooler (Port 6543).
    *   **Event Bus**: **Upstash QStash** (HTTP Queue).
    *   **Compute**: **Cloud Run** (Worker) and **Vercel** (Core).
3.  **Balance SOLID with Simplicity (YAGNI)**:
    *   **Monorepo**: We use a single repository. The `shared` directory is copied into the Worker's Docker image at build time.
    *   **No Frameworks for AI**: We use the raw `openai` library instead of LangChain.

## Technology Stack & Infrastructure
### 1. Compute & Runtime Layers
*   **Core Service**: **Python (FastAPI)**
    *   **Responsibility**: User API Gateway, Authentication, Job Creation.
    *   **Hosting**: Vercel (Serverless Functions).
*   **Worker Service**: **Python (FastAPI)**
    *   **Responsibility**: AI Pipeline Executor (YouTube -> Transcript -> GPT-4o -> Notion).
    *   **Hosting**: Cloud Run (CPU allocated only during request processing).
    *   **Security**: Verifies `Upstash-Signature` header.

### 2. Event Bus (The Nervous System)
*   **Service**: **Upstash QStash**
*   **Role**: Reliable asynchronous job delivery.
*   **Configuration**:
    *   **Retries**: 3 times (Exponential Backoff).
    *   **Timeout**: 1 hour (matching Cloud Run limit).
*   **Protocol**:
    *   **Core**: Publishes JSON payload to QStash.
    *   **Worker**: Receives HTTP POST from QStash.

### 3. Data Persistence (The Memory)
*   **Database**: **Supabase (PostgreSQL)**
    *   **Role**: Relational data storage.
    *   **Configuration**: **Transaction Mode (Port 6543)**.
    *   **Rationale**: Essential for handling high concurrency from serverless workers without `max_connections` errors.
*   **ORM**: **SQLModel (SQLAlchemy + Pydantic)**
    *   **Role**: Async ORM.

### Architecture Structure
```
flashnote-ai/
├── core/               # FastAPI (User Facing)
│   ├── api/            # Routes (Auth, Notes)
│   └── main.py         # App Entrypoint
├── worker/             # FastAPI (Internal Job Handler)
│   ├── api/            # Routes (Webhooks)
│   ├── services/       # OpenAI, YouTube, Notion Logic
│   ├── Dockerfile      # Multi-stage build (copies shared)
│   └── main.py         # App Entrypoint
└── shared/             # Shared Library
    ├── models/         # SQLModel Database Models
    ├── schemas/        # Pydantic API/Event Schemas
    └── utils/          # Common utilities
```

### Implementation Approach: YAGNI
1.  **Schema First**: We define the `JobRequest` schema in `shared`.
2.  **Env Strategy**: Single `.env` for local. CI/CD injects secrets.
3.  **No Premature Optimization**: No caching layers yet.

### Layer Responsibilities & Event Bus Integration
#### 1. Core Service (Python/FastAPI)
*(The Manager)*
*   **Responsibility**:
    1.  Validate `POST /notes` request.
    2.  Create `Note` record in DB (Status: `PENDING`).
    3.  **Publish** job to QStash (`POST https://qstash.upstash.io/v1/publish/...`).
    4.  Return `202 Accepted` to user.
*   **Event Bus Usage**: Publisher.

#### 2. Worker Service (Python/FastAPI)
*(The Specialist)*
*   **Responsibility**:
    1.  Receive `POST /webhooks/process-job`.
    2.  **Verify Signature**: Check `Upstash-Signature`.
    3.  **Idempotency Check**: If Note is already `COMPLETED`, return 200 immediately.
    4.  Fetch Transcript & Generate Content (GPT-4o).
    5.  Generate Mermaid Diagram.
    6.  Create Notion Page.
    7.  Update DB `Note` (Status: `COMPLETED`).
*   **Event Bus Usage**: Receiver (Webhook).

#### 3. Event Bus (Upstash QStash)
*   **Mechanism**: HTTP Push.
*   **Connectivity**: REST API.

### Test-Driven Development (TDD)
#### Testing Strategy
*   **Unit Tests**:
    *   **Core**: Mock `QStashClient`.
    *   **Worker**: Test AI Services using mocked OpenAI responses.
*   **Integration Tests**:
    *   Use `ngrok` to expose local Worker to QStash (or use local emulator) for E2E testing.

#### TDD Cycle
1.  🔴 **Red**: Write a test for `POST /notes` asserting it calls QStash.
2.  🟡 **Yellow**: Implement the endpoint and QStash integration.
3.  🟢 **Green**: Refactor and add error handling.

### Code Quality Guidelines
1.  **Dependency Inversion**: Services must be injected.
2.  **Stateless Agents**: The Worker must be stateless.
3.  **Configuration**: Fail fast if `QSTASH_CURRENT_SIGNING_KEY` or `DATABASE_URL` is missing.

### Codebase Guide Maintenance
We will maintain a `CODEBASE_GUIDE.md`.

#### CODEBASE_GUIDE.md Structure
```markdown
# Codebase Guide
## Event Schema Registry
- `JobRequest`: { video_url: str, user_id: str, options: dict }
## Infrastructure Configuration
- QStash Topic: `flashnote-jobs`
- DB Connection: Transaction Pooler (6543)
## Current Status
- [ ] Core Setup
- [ ] Worker Setup
```

### Git Workflow (git-worktree)
*Standard git-worktree workflow applies.*
We use a Monorepo strategy.

## Implementation Rules

### 1. Domain Entities & ORM
**Rule**: When a domain entity corresponds to a Database document, **do not manually redefine the interface**. Directly import and use the types generated by the ORM (SQLModel).

```python
# ✅ Correct Example
from shared.models import Note

# In API Route
@app.post("/notes")
async def create_note(note: Note, session: AsyncSession):
    session.add(note)
    await session.commit()
    return note
```
