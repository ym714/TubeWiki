# Implementation Plan - FlashNote AI

This plan is derived from [technical_spec.md](file:///Users/motoki/projects/TubeWiki/technical_spec.md) and focuses on the Backend Architecture (Core, Worker, Shared).
**Philosophy**: Atomic Commits & Continuous Push.

## Phase 1: Project Scaffolding & Shared Library
**Goal**: Set up the Monorepo structure and define the shared contract (Schemas & Models) between Core and Worker.

### Step 1.1: Initialize Monorepo Structure
- **Action**: Create directories `core`, `worker`, `shared` and their subdirectories (`api`, `services`, `models`, `schemas`, `utils`). Create empty `__init__.py` files.
- **Code/Details**:
    - `mkdir -p core/api worker/api worker/services shared/models shared/schemas shared/utils`
    - `touch core/__init__.py worker/__init__.py shared/__init__.py ...`
- **Verification**: `ls -R` shows the structure.
- **🛑 Git Operation**:
  ```bash
  git add .
  git commit -m "chore(project): initialize monorepo structure (Step 1.1)"
  git push origin main
  ```

### Step 1.2: Define Dependencies
- **Action**: Create [requirements.txt](file:///Users/motoki/projects/TubeWiki/requirements.txt) with all necessary libraries (`fastapi`, `sqlmodel`, `asyncpg`, `openai`, `upstash-qstash`, `youtube-transcript-api`, `python-dotenv`).
- **Code/Details**: See [technical_spec.md](file:///Users/motoki/projects/TubeWiki/technical_spec.md) for stack.
- **Verification**: `pip install -r requirements.txt` works.
- **🛑 Git Operation**:
  ```bash
  git add requirements.txt
  git commit -m "chore(deps): add requirements.txt (Step 1.2)"
  git push origin main
  ```

### Step 1.3: Shared - JobRequest Schema
- **Action**: Create [shared/schemas/job.py](file:///Users/motoki/projects/TubeWiki/shared/schemas/job.py).
- **Code/Details**: Define [JobRequest](file:///Users/motoki/projects/TubeWiki/shared/schemas/job.py#4-9) Pydantic model (`video_url`, `user_id`, `options`).
- **Verification**: `python -c "from shared.schemas.job import JobRequest; print(JobRequest(video_url='x', user_id='y'))"`
- **🛑 Git Operation**:
  ```bash
  git add shared/schemas/job.py
  git commit -m "feat(shared): define JobRequest schema (Step 1.3)"
  git push origin main
  ```

### Step 1.4: Shared - Database Models
- **Action**: Create [shared/models/note.py](file:///Users/motoki/projects/TubeWiki/shared/models/note.py) and [shared/models/user.py](file:///Users/motoki/projects/TubeWiki/shared/models/user.py).
- **Code/Details**: Define [Note](file:///Users/motoki/projects/TubeWiki/shared/models/note.py#12-24) (SQLModel) with `status` enum (PENDING, COMPLETED, etc.) and [User](file:///Users/motoki/projects/TubeWiki/shared/models/user.py#5-12) model.
- **Verification**: `python -c "from shared.models.note import Note"`
- **🛑 Git Operation**:
  ```bash
  git add shared/models/
  git commit -m "feat(shared): define Note and User DB models (Step 1.4)"
  git push origin main
  ```

### Step 1.5: Shared - Database Connection
- **Action**: Create [shared/db.py](file:///Users/motoki/projects/TubeWiki/shared/db.py).
- **Code/Details**: Setup `create_async_engine` and [get_session](file:///Users/motoki/projects/TubeWiki/shared/db.py#20-26) dependency. Use `DATABASE_URL` env var.
- **Verification**: Import [get_session](file:///Users/motoki/projects/TubeWiki/shared/db.py#20-26) successfully.
- **🛑 Git Operation**:
  ```bash
  git add shared/db.py
  git commit -m "feat(shared): setup async db connection (Step 1.5)"
  git push origin main
  ```

## Phase 2: Core Service Implementation
**Goal**: Implement the User API to handle Note creation and Job dispatching.

### Step 2.1: Core Configuration
- **Action**: Create [core/config.py](file:///Users/motoki/projects/TubeWiki/core/config.py).
- **Code/Details**: Load `DATABASE_URL`, `QSTASH_TOKEN`, `QSTASH_URL`, `WORKER_URL`. Add validation.
- **Verification**: `python -c "from core.config import config; config.validate()"` (Expect error if env missing).
- **🛑 Git Operation**:
  ```bash
  git add core/config.py
  git commit -m "feat(core): add configuration module (Step 2.1)"
  git push origin main
  ```

### Step 2.2: QStash Service (Publisher)
- **Action**: Create [core/services/qstash.py](file:///Users/motoki/projects/TubeWiki/core/services/qstash.py).
- **Code/Details**: Implement [publish_job(job: JobRequest)](file:///Users/motoki/projects/TubeWiki/core/services/qstash.py#14-31). Use `httpx` to POST to QStash.
- **Verification**: Mock test or manual verification.
- **🛑 Git Operation**:
  ```bash
  git add core/services/qstash.py
  git commit -m "feat(core): implement QStash publisher service (Step 2.2)"
  git push origin main
  ```

### Step 2.3: POST /notes Endpoint
- **Action**: Create [core/api/notes.py](file:///Users/motoki/projects/TubeWiki/core/api/notes.py).
- **Code/Details**:
    - Accept [JobRequest](file:///Users/motoki/projects/TubeWiki/shared/schemas/job.py#4-9).
    - Create [Note](file:///Users/motoki/projects/TubeWiki/shared/models/note.py#12-24) in DB (PENDING).
    - Call `qstash_service.publish_job`.
    - Return 202 Accepted.
- **Verification**: Unit test mocking DB and QStash.
- **🛑 Git Operation**:
  ```bash
  git add core/api/notes.py
  git commit -m "feat(core): implement POST /notes endpoint (Step 2.3)"
  git push origin main
  ```

### Step 2.4: Core Entrypoint
- **Action**: Create [core/main.py](file:///Users/motoki/projects/TubeWiki/core/main.py).
- **Code/Details**: Setup FastAPI app, include router, add `/healthz`.
- **Verification**: `uvicorn core.main:app --reload` starts successfully.
- **🛑 Git Operation**:
  ```bash
  git add core/main.py
  git commit -m "feat(core): setup application entrypoint (Step 2.4)"
  git push origin main
  ```

## Phase 3: Worker Service Implementation
**Goal**: Implement the AI processing worker with security and robustness.

### Step 3.1: Worker Configuration
- **Action**: Create [worker/config.py](file:///Users/motoki/projects/TubeWiki/worker/config.py).
- **Code/Details**: Load `OPENAI_API_KEY`, `QSTASH_CURRENT_SIGNING_KEY`, `QSTASH_NEXT_SIGNING_KEY`.
- **Verification**: Validate config loading.
- **🛑 Git Operation**:
  ```bash
  git add worker/config.py
  git commit -m "feat(worker): add configuration module (Step 3.1)"
  git push origin main
  ```

### Step 3.2: Security (Signature Verification)
- **Action**: Create [worker/services/security.py](file:///Users/motoki/projects/TubeWiki/worker/services/security.py).
- **Code/Details**: Use `upstash_qstash` receiver to verify `Upstash-Signature` header.
- **Verification**: Unit test with valid/invalid signatures.
- **🛑 Git Operation**:
  ```bash
  git add worker/services/security.py
  git commit -m "feat(worker): implement QStash signature verification (Step 3.2)"
  git push origin main
  ```

### Step 3.3: YouTube Service
- **Action**: Create [worker/services/youtube.py](file:///Users/motoki/projects/TubeWiki/worker/services/youtube.py).
- **Code/Details**: Implement [get_transcript(video_url)](file:///Users/motoki/projects/TubeWiki/worker/services/youtube.py#26-38). Handle URL parsing and `youtube_transcript_api`.
- **Verification**: Test with a real YouTube URL.
- **🛑 Git Operation**:
  ```bash
  git add worker/services/youtube.py
  git commit -m "feat(worker): implement YouTube transcript service (Step 3.3)"
  git push origin main
  ```

### Step 3.4: AI Service (GPT-4o)
- **Action**: Create [worker/services/ai.py](file:///Users/motoki/projects/TubeWiki/worker/services/ai.py).
- **Code/Details**: Implement [generate_note_content(transcript)](file:///Users/motoki/projects/TubeWiki/worker/services/ai.py#11-46) and [generate_diagram(content)](file:///Users/motoki/projects/TubeWiki/worker/services/ai.py#47-80). Use `openai` async client.
- **Verification**: Mock OpenAI response.
- **🛑 Git Operation**:
  ```bash
  git add worker/services/ai.py
  git commit -m "feat(worker): implement GPT-4o generation service (Step 3.4)"
  git push origin main
  ```

### Step 3.5: Webhook Handler (Process Job)
- **Action**: Create [worker/api/webhook.py](file:///Users/motoki/projects/TubeWiki/worker/api/webhook.py).
- **Code/Details**:
    - Verify Signature.
    - **Idempotency Check**: Check if Note is COMPLETED.
    - Execute Pipeline: YouTube -> AI -> DB Update.
    - Handle Errors (Update DB to FAILED).
- **Verification**: Simulate POST request.
- **🛑 Git Operation**:
  ```bash
  git add worker/api/webhook.py
  git commit -m "feat(worker): implement job processing webhook (Step 3.5)"
  git push origin main
  ```

### Step 3.6: Worker Entrypoint & Dockerfile
- **Action**: Create [worker/main.py](file:///Users/motoki/projects/TubeWiki/worker/main.py) and `worker/Dockerfile`.
- **Code/Details**:
    - [main.py](file:///Users/motoki/projects/TubeWiki/core/main.py): FastAPI app setup.
    - `Dockerfile`: Multi-stage build. **Crucial**: Copy `shared/` directory into the image.
- **Verification**: Build Docker image.
- **🛑 Git Operation**:
  ```bash
  git add worker/main.py worker/Dockerfile
  git commit -m "feat(worker): setup entrypoint and Dockerfile (Step 3.6)"
  git push origin main
  ```

## Phase 4: Notion Integration (Week 2 Scope)
**Goal**: Integrate with Notion API to push generated notes.

### Step 4.1: Notion Service
- **Action**: Create `worker/services/notion.py`.
- **Code/Details**: Implement `create_page(token, page_id, content)`. Handle Block conversion (Markdown to Notion Blocks).
- **Verification**: Test creating a page in Notion.
- **🛑 Git Operation**:
  ```bash
  git add worker/services/notion.py
  git commit -m "feat(worker): implement Notion API integration (Step 4.1)"
  git push origin main
  ```

### Step 4.2: Integrate Notion into Webhook
- **Action**: Update [worker/api/webhook.py](file:///Users/motoki/projects/TubeWiki/worker/api/webhook.py).
- **Code/Details**: Call `notion_service.create_page` after AI generation. Update Note with Notion URL.
- **Verification**: Full E2E test.
- **🛑 Git Operation**:
  ```bash
  git add worker/api/webhook.py
  git commit -m "feat(worker): integrate Notion push into job pipeline (Step 4.2)"
  git push origin main
  ```
