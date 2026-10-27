# ERP/CRM Backend Practical Interview (Candidate Copy)

## Purpose
This is a deliberately incomplete FastAPI + PostgreSQL mini-backend. Use Google Antigravity if you like, but explain your reasoning and verify changes.

## Start PostgreSQL
Docker is required for the supplied database setup:
```bash
docker compose up -d db
```
Wait until the database health check passes.

## Run the API
```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

The default DB URL uses localhost port 5433. You can override it with the `DATABASE_URL` environment variable.

## Candidate tasks
1. Verify both `/health` and `/health/db`; explain what each proves and what it does not prove.
2. Fix incorrect product pagination/count behavior. Add validation for `limit`, `offset`, SKU, and stock.
3. Make missing-order responses use correct HTTP status codes.
4. Implement a safe order workflow:
   - reject quantity <= 0
   - validate customer and product
   - prevent overselling under concurrent requests
   - ensure stock deduction and order insertion are atomic
   - rollback cleanly on errors
5. Add a `GET /orders` endpoint with pagination and optional status filter.
6. Add tests for successful order creation, missing customer/product, invalid quantity, insufficient stock, and database health.
7. Explain what you would change for a multi-tenant ERP, role-based permissions, audit logs, migrations, and large datasets.

## Interview rules
- AI tools are allowed; think aloud and review diffs.
- Don't blindly replace the whole project.
- The interviewer may ask you to explain any function or alter a requirement.
- The app uses PostgreSQL, not a fake in-memory database.
