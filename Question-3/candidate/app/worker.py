import json
import time
from sqlalchemy import select
from .db import SessionLocal
from .models import Job, AuditEvent

# Simulated processing. Never fetches the supplied URL.
def extract_document(url: str) -> dict:
    time.sleep(0.15)
    if "permanent-failure" in url:
        raise ValueError("unsupported document")
    if "temporary-failure" in url:
        raise ConnectionError("extraction service unavailable")
    if "crash-after-start" in url:
        raise RuntimeError("simulated worker crash after start")
    return {"source": url, "pages": 2, "fields": {"invoice_number": "INV-1001"}}

def process_one(job_id: int):
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job or job.status == "cancelled":
            return
        # BUG: read-then-write state transition is not atomic; concurrent workers can both process.
        job.status = "processing"
        job.attempts += 1
        db.commit()
        try:
            result = extract_document(job.document_url)
            # BUG: stale ORM object can overwrite a cancellation or another worker's result.
            job.result = json.dumps(result)
            job.status = "completed"
            job.error = None
            db.add(AuditEvent(job_id=job.id, message="document processed"))
            db.commit()
        except Exception as exc:
            # BUG: permanent errors retry forever and raw internal details are persisted.
            job.error = str(exc)
            job.status = "queued"
            db.commit()

def main():
    print("SQLite polling worker ready. Press Ctrl+C to stop.")
    while True:
        with SessionLocal() as db:
            # BUG: no claim/lock/lease; multiple workers may select the same job.
            job_ids = list(db.scalars(select(Job.id).where(Job.status == "queued").order_by(Job.created_at).limit(10)))
        for job_id in job_ids:
            process_one(job_id)
        time.sleep(1)

if __name__ == "__main__":
    main()
