#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulldoggy Reminders App Mini Implementation
Based on AutomationPanda/bulldoggy-reminders-app
Created: 2023-11-15
Description: A simplified FastAPI implementation with TinyDB backend
that mimics the core reminder functionality of Bulldoggy app.
"""

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, List
from pydantic import BaseModel
from tinydb import TinyDB, Query
import json
import base64
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Security setup
security = HTTPBasic()

# Configuration
CONFIG_FILE = Path("config.json")
DB_FILE = Path("reminder_db.json")

# Load config
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(json.dumps({
        "users": {"pythonista": base64.b64encode("I<3testing".encode()).decode()},
        "db_path": str(DB_FILE)
    }))
config = json.loads(CONFIG_FILE.read_text())

# Initialize DB
db = TinyDB(config["db_path"])
reminders_table = db.table("reminders")

# HTML Templates
templates = Jinja2Templates(directory="templates")

# Models
class Reminder(BaseModel):
    list_name: str
    item_text: str
    completed: bool = False

# Helper functions
def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify basic auth credentials against config"""
    correct_username = config["users"].get(credentials.username)
    if not correct_username:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    correct_password = base64.b64decode(correct_username).decode()
    if credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return credentials.username

def get_user_reminders(username: str) -> Dict[str, List[Dict]]:
    """Get all reminders for a user"""
    ReminderQuery = Query()
    user_reminders = reminders_table.search(ReminderQuery.user == username)
    
    # Group by list
    lists = {}
    for rem in user_reminders:
        if rem["list_name"] not in lists:
            lists[rem["list_name"]] = []
        lists[rem["list_name"]].append({
            "text": rem["item_text"],
            "completed": rem["completed"]
        })
    return lists

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main app page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/reminders")
async def get_reminders(username: str = Depends(verify_user)):
    """Get all reminders for authenticated user"""
    return get_user_reminders(username)

@app.post("/api/reminders")
async def create_reminder(reminder: Reminder, username: str = Depends(verify_user)):
    """Create a new reminder"""
    reminders_table.insert({
        "user": username,
        "list_name": reminder.list_name,
        "item_text": reminder.item_text,
        "completed": reminder.completed
    })
    return {"status": "success"}

@app.delete("/api/reminders/{list_name}")
async def delete_list(list_name: str, username: str = Depends(verify_user)):
    """Delete