from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
@app.get("/")
def read_root():
    return {"message":"hello fastapi from mac","status":"success"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"greeting": f"hello,{name}! welcome fastapi world"}

#模拟你刚刚在 Flask 项目里做过的“任务管理”数据
fake_tasks_db = [
    {"id": 1, "title": "学习 FastAPI 基础", "minutes": 60, "done": True},
    {"id": 2, "title": "攻克 Pydantic 数据验证", "minutes": 45, "done": False}
]

# 1. 写一个获取所有任务的接口 (GET)
@app.get("/api/tasks")
def get_tasks():
    return {
        "status": "success",
        "total": len(fake_tasks_db),
        "data": fake_tasks_db
    }

@app.get("/api/user/profile")
def get_user_profile():
    return {
        "code": 200,
        "message": "get user profile",
        "data": {
            "username": "jerry",
            "level": 3,
            "is_active": True,
            "skills": ["python","fastapi","restful api"],
            "recent_task": {
               "id": 1,
               "title": "finish json and api rule",
               "completed": False
            }
        }
    }

class TaskCreate(BaseModel):
    title: str
    minutes: int
    done: bool = False

@app.post("/api/tasks")
def create_task(task: TaskCreate):
    return {
        "status":"success",
        "message": "new tasks success",
        "create_data": task
    }