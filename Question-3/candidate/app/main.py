from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import Job
from .queue import publish

app = FastAPI(title="Blackbox Job Orchestrator - Intentionally Buggy")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

class CreateJob(BaseModel):
    tenant_id: str
    document_url: str
    idempotency_key: str

class JobOut(BaseModel):
    id: int
    tenant_id: str
    document_url: str
    status: str
    attempts: int
    result: str | None
    error: str | None
    model_config = {"from_attributes": True}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/jobs", response_model=JobOut, status_code=201)
def create_job(payload: CreateJob, db: Session = Depends(get_db)):
    existing = db.scalar(select(Job).where(Job.idempotency_key == payload.idempotency_key))
    if existing:
        return existing
    job = Job(tenant_id=payload.tenant_id, document_url=payload.document_url, idempotency_key=payload.idempotency_key)
    db.add(job)
    db.commit()
    db.refresh(job)
    publish(job.id)
    return job

@app.get("/jobs", response_model=list[JobOut])
def list_jobs(tenant_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return list(db.scalars(select(Job).where(Job.tenant_id == tenant_id).offset(offset).limit(limit)))

@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Not found")
    return job

@app.post("/jobs/{job_id}/cancel", response_model=JobOut)
def cancel_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Not found")
    job.status = "cancelled"
    db.commit()
    db.refresh(job)
    return job

@app.post("/jobs/{job_id}/retry", response_model=JobOut)
def retry_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Not found")
    job.status = "queued"
    job.error = None
    db.commit()
    publish(job.id)
    db.refresh(job)
    return job
