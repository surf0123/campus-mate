from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import create_todo, delete_todo, init_db, list_todos, update_todo_done
from weather import get_weather_today

app = FastAPI(title="Campus Mate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoCreate(BaseModel):
    title: str
    due_date: str | None = None


class TodoUpdate(BaseModel):
    done: bool


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/weather/today")
def weather_today() -> dict:
    try:
        weather = get_weather_today()
    except Exception:
        raise HTTPException(
            status_code=502, detail="날씨 정보를 가져오지 못했습니다"
        ) from None
    if weather is None:
        raise HTTPException(status_code=502, detail="날씨 정보를 가져오지 못했습니다")
    return weather


@app.get("/todos")
def get_todos() -> list[dict]:
    return list_todos()


@app.post("/todos", status_code=201)
def post_todo(todo: TodoCreate) -> dict:
    return create_todo(todo.title, todo.due_date)


@app.patch("/todos/{todo_id}")
def patch_todo(todo_id: int, update: TodoUpdate) -> dict:
    row = update_todo_done(todo_id, update.done)
    if row is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return row


@app.delete("/todos/{todo_id}", status_code=204)
def remove_todo(todo_id: int) -> None:
    if not delete_todo(todo_id):
        raise HTTPException(status_code=404, detail="todo not found")
