from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Interview Task API")

# Temporary in-memory storage for this interview.
tasks = [
    {"id": 1, "title": "Learn FastAPI", "completed": False},
    {"id": 2, "title": "Write unit tests", "completed": True},
]
next_id = 3


class TaskCreate(BaseModel):
    title: str
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(status: str | None = None, search: str | None = None):
    result = tasks

    if status:
        result = [
            task for task in result
            if task["completed"] == (status == "completed")
        ]

    if search:
        result = [
            task for task in result
            if search in task["title"]
        ]

    return {"items": result, "count": len(tasks)}


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return {"error": "Task not found"}


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    global next_id

    task = {
        "id": next_id,
        "title": payload.title,
        "completed": payload.completed,
    }
    tasks.append(task)
    next_id += 1
    return task


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            data = payload.model_dump()
            task.update(data)
            return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {"message": "Deleted"}

    raise HTTPException(status_code=404, detail="Task not found")
