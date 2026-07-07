from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.models import Task

app = FastAPI(title="Task Manager API")

tasks: dict[int, Task] = {}
_next_id: int = 1


class TaskCreate(BaseModel):
    title: str
    description: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int = 100, offset: int = 0) -> list[Task]:
    # BUG 1: ignores done filter — always returns all tasks regardless of ?done=
    # BUG 2: ignores limit/offset — pagination params accepted but not applied
    return list(tasks.values())


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> Task:
    global _next_id
    task = Task(id=_next_id, title=body.title, description=body.description)
    tasks[_next_id] = task
    _next_id += 1
    return task


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id].done = True
    return tasks[task_id]
