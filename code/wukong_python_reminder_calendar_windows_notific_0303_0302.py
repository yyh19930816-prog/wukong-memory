#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulldoggy Reminders App Mini Implementation
学习来源: AutomationPanda/bulldoggy-reminders-app (GitHub)
日期: 2023-11-11
功能描述: 一个简易版的Bulldoggy提醒应用，使用FastAPI和TinyDB实现基本的提醒列表功能，
         支持用户登录、创建/删除列表、添加/完成/删除提醒事项。
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pathlib import Path
import json
from tinydb import TinyDB, Query

# 初始化应用和组件
app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 加载配置
CONFIG_FILE = "config.json"
DB_FILE = "reminder_db.json"

# 从配置文件加载用户凭证
with open(CONFIG_FILE) as f:
    config = json.load(f)
    users = config.get("users", {"pythonista": "I<3testing"})

# 初始化TinyDB数据库
db = TinyDB(DB_FILE)
reminders_table = db.table("reminders")

# 验证用户凭据
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if users.get(username) != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

# 首页路由 - 显示提醒列表
@app.get("/")
async def home(request: Request, username: str = Depends(authenticate_user)):
    # 获取该用户的所有提醒列表
    user_reminders = reminders_table.search(Query().user == username)
    lists = {r["list_name"] for r in user_reminders}
    
    # 获取第一个列表的条目（如果有）
    active_list = next(iter(lists), None)
    items = [
        r["item"] for r in user_reminders 
        if r["list_name"] == active_list
    ] if active_list else []
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "lists": lists,
            "active_list": active_list,
            "items": items,
        },
    )

# 添加新提醒列表
@app.post("/lists")
async def add_list(list_name: str, username: str = Depends(authenticate_user)):
    if not reminders_table.search(
        Query().user == username and Query().list_name == list_name
    ):
        reminders_table.insert({"user": username, "list_name": list_name, "item": ""})
    return {"status": "ok"}

# 添加提醒事项
@app.post("/items")
async def add_item(
    list_name: str, 
    item: str, 
    username: str = Depends(authenticate_user)
):
    reminders_table.insert({"user": username, "list_name": list_name, "item": item})
    return {"status": "ok"}

# 删除提醒事项
@app.delete("/items")
async def delete_item(
    list_name: str, 
    item: str, 
    username: str = Depends(authenticate_user)
):
    reminders_table.remove(
        (Query().user == username) & 
        (Query