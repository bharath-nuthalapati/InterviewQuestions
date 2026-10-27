# FastAPI Practical Interview — Candidate Brief

## Goal
Debug and extend this FastAPI Task Manager API. You may use Google Antigravity and AI tools, but you must explain every change and verify it.

## Setup
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `uvicorn main:app --reload`
4. Open `http://127.0.0.1:8000/docs`

## Tasks
1. Inspect the existing code and explain the data flow.
2. Fix bugs in filtering, search, counts, missing-task handling, and input validation.
3. Implement `GET /tasks/stats` returning total, completed, and pending counts.
4. Make PATCH update only fields the client actually supplied.
5. Add tests for success cases and edge cases.
6. Explain how you would replace in-memory storage with a database.

## Interview rules
- AI assistance is allowed. Think aloud before and after prompting.
- Do not blindly replace the whole project.
- The interviewer may ask you to explain or modify any function.
- Prioritize correctness, validation, status codes, and tests over adding features.
