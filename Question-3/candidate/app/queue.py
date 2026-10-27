"""Intentionally simplistic queue adapter.

The app persists queued jobs in SQLite. publish() is intentionally a no-op,
so the worker must discover queued jobs from the database. Candidates should
reason about the durability/latency trade-off and make dispatch/recovery robust.
"""
def publish(job_id: int):
    # BUG: no durable dispatch signal; API assumes this is enough.
    return None
