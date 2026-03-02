#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulldoggy Reminders App Core Implementation
学习来源: AutomationPanda/bulldoggy-reminders-app
日期: 2023-11-29
功能描述: 基于FastAPI和TinyDB实现的简单提醒事项应用核心功能
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from tinydb import TinyDB, Query
import uvicorn
import json
import os

# 应用初始化
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 数据库配置
DB_PATH = "reminder_db.json"
db = TinyDB(DB_PATH)
reminders_table = db.table("reminders")

# 用户模型
class User(BaseModel):
    username: str
    password: str

# 提醒事项模型
class Reminder(BaseModel):
    id: Optional[int] = None
    list_name: str
    item_text: str
    completed: bool = False

# 加载配置文件
def load_config():
    with open("config.json") as f:
        return json.load(f)

# 用户认证
def authenticate_user(username: str, password: str):
    config = load_config()
    return username in config["users"] and config["users"][username] == password

# API端点
@app.get("/")
async def read_root(request: Request):
    """首页重定向到登录页"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(user: User):
    """用户登录"""
    if not authenticate_user(user.username, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@app.get("/reminders")
async def get_reminders():
    """获取所有提醒事项"""
    return {"reminders": reminders_table.all()}

@app.post("/reminders")
async def add_reminder(reminder: Reminder):
    """添加新提醒事项"""
    reminder.id = len(reminders_table) + 1
    reminders_table.insert(reminder.dict())
    return {"message": "Reminder added", "reminder": reminder}

@app.put("/reminders/{reminder_id}")
async def update_reminder(reminder_id: int, reminder: Reminder):
    """更新提醒事项"""
    reminder.id = reminder_id
    query = Query().id == reminder_id
    reminders_table.update(reminder.dict(), query)
    return {"message": "Reminder updated", "reminder": reminder}

@app.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: int):
    """删除提醒事项"""
    query = Query().id == reminder_id
    reminders_table.remove(query)
    return {"message": "Reminder deleted"}

# 主程序入口
if __name__ == "__main__":
    # 创建示例数据库文件
    if not os.path.exists(DB_PATH):
        reminders_table.insert({"list_name": "Shopping", "item_text": "Buy milk", "completed": False})
    
    # 启动FastAPI应用
    uvicorn.run(app, host="127.0.0.1", port=8000)