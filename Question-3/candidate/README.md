# Blackbox: Advanced FastAPI Job Orchestrator (No Docker)

**Timebox:** 90–120 minutes. AI tools, including Google Antigravity, are allowed.

This is an intentionally broken FastAPI + SQLAlchemy application. It uses a local SQLite database and a database-polling worker so the exercise works on an ordinary Windows, macOS, or Linux laptop. **Docker, PostgreSQL, and Redis are not required.** Document extraction is simulated; the code never fetches the supplied URL.

## Setup

Install Python 3.11+ (3.12 recommended), then from this folder:

### Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. In a second terminal, activate the same virtual environment and run:

```bash
python -m app.worker
```

SQLite database `jobs.db` is created in this folder when the app starts. To reset the test data, stop the API and worker, then delete `jobs.db`.

Example request:
```json
POST /jobs
{
  "tenant_id": "acme",
  "document_url": "https://example.com/invoice.pdf",
  "idempotency_key": "submission-001"
}
```

For the exercise, send `X-Tenant-ID: acme` as the simulated authenticated tenant header when using routes that require tenant identity. Do not assume a caller-supplied tenant field is proof of identity.

## Your assignment

Find and fix hidden reliability, correctness, security, and concurrency defects. Preserve the public API wherever reasonable; do not replace the project wholesale.

1. Enforce tenant isolation on all read/write routes. `X-Tenant-ID` represents a trusted identity supplied by the test harness; explain what production authentication would require.
2. Repeated submission with the same idempotency key in one tenant must not create duplicate jobs. Same key + different input must conflict. Different tenants can reuse keys.
3. Ensure queued jobs are eventually discovered after API restarts and avoid relying on an in-memory queue. Explain the trade-off of database polling versus a dedicated broker.
4. Multiple workers and duplicate work must not process a job concurrently. Define what happens if a worker crashes after a side effect.
5. Implement bounded retries with backoff. Permanent failures must not retry forever.
6. Cancellation and completion must not overwrite each other. Define legal state transitions.
7. Prevent arbitrary untrusted document URLs from being fetched. The current extractor is simulated; do not add fetching without a safe design. URL parsing alone does not prevent DNS rebinding or SSRF.
8. Avoid exposing raw exception details; validate pagination and provide stable ordering.
9. Add tests for overlapping workers, duplicate requests, cross-tenant access, permanent/transient failures, cancellation races, and restart/recovery.

## Built-in fault cases

- Include `temporary-failure` in the URL to simulate a transient failure.
- Include `permanent-failure` to simulate a permanent failure.
- Include `crash-after-start` to simulate a worker failure after the job is marked processing.

## Demo

Show API requests, SQLite database state, a worker run, tests, and explain each fix. Note remaining limitations. A full production-grade system is not expected in the timebox; a correct vertical slice and sound reasoning matter most.
