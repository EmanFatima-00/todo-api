from fastapi import FastAPI, HTTPException
from database import init_db, get_db
import psycopg2.extras
from pydantic import BaseModel

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

class Task(BaseModel):
    id: int
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    title: str

@app.get("/")
def ghar():
    return {"message": "To-Do API chal rahi hai"}

@app.get("/health")
def health():
    return {"status": "ok"}

# 1. GET ALL TASKS
@app.get("/tasks", response_model=list[Task])
def get_tasks():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT * FROM tasks")
    rows = c.fetchall()
    conn.close()
    return rows

# 2. GET 1 TASK
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = c.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row

# 3. POST - NAYA TASK BANANA
@app.post("/tasks", response_model=Task, status_code=201)
def naya_task_add_karo(task: TaskCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, done) VALUES (%s,%s) RETURNING id", (task.title, False))
    new_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, "title": task.title, "done": False}

# 4. PUT - TASK UPDATE KARNA
@app.put("/tasks/{task_id}", response_model=Task)
def task_complete_karo(task_id: int, task: Task):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s", (task.title, task.done, task_id))
    conn.commit()
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.close()
    return {"id": task_id, "title": task.title, "done": task.done}

# 5. DELETE - TASK DELETE KARNA
@app.delete("/tasks/{task_id}", status_code=204)
def task_delete_karo(task_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.close()
    return