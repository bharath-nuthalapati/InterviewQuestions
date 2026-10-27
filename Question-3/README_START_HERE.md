# Interviewer: Advanced Antigravity Debug Challenge (No Docker)

Give candidates only the `candidate/` folder. Keep `interviewer_private/` private.

**No Docker, PostgreSQL, or Redis required.** Candidate setup uses Python + pip, FastAPI, SQLAlchemy, and SQLite. Allow 90–120 minutes and permit Google Antigravity, but require the candidate to run tests and explain their code.

Suggested interview flow:
1. 10 minutes: architecture walkthrough.
2. 30 minutes: fix API correctness and tenant isolation.
3. 20 minutes: retry, cancellation, and worker state handling.
4. 20 minutes: overlapping-worker and recovery tests.
5. 10 minutes: explain limits and production migration path.

Important: SQLite is deliberately used to lower setup friction. Ask candidates to explain which locking, concurrency, and multi-instance guarantees would need to change or be revalidated before production deployment on PostgreSQL and/or a message broker.
