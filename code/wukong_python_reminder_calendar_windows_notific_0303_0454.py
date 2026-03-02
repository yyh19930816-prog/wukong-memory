"""
Bulldoggy Reminders App Implementation
Based on AutomationPanda/bulldoggy-reminders-app README
Created: 2023-10-15
A simple FastAPI-based reminders web app with HTMX frontend and TinyDB backend.
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from tinydb import TinyDB, Query
import json
import os

# Initialize FastAPI app
app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Database configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

try:
    with open(config_path) as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"database_path": "reminder_db.json", "users": {"pythonista": "I<3testing"}}

db = TinyDB(config["database_path"])
reminders_table = db.table("reminders")

# Data Models
class Reminder(BaseModel):
    id: Optional[int] = None
    list_name: str
    description: str
    completed: bool = False

class ReminderList(BaseModel):
    name: str
    reminders: List[Reminder] = []

# Authentication dependency
def authenticate_user(username: str, password: str):
    if username not in config["users"] or config["users"][username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API Routes
@app.post("/api/reminders/")
async def create_reminder(reminder: Reminder):
    """Create a new reminder"""
    reminder_id = reminders_table.insert(reminder.dict())
    return {"id": reminder_id, **reminder.dict()}

@app.get("/api/reminders/", response_model=List[ReminderList])
async def get_reminders():
    """Get all reminders grouped by list"""
    reminders = reminders_table.all()
    lists = {}
    for reminder in reminders:
        if reminder["list_name"] not in lists:
            lists[reminder["list_name"]] = []
        lists[reminder["list_name"]].append(reminder)
    return [ReminderList(name=k, reminders=v) for k, v in lists.items()]

@app.get("/api/reminders/{list_name}", response_model=ReminderList)
async def get_reminders_by_list(list_name: str):
    """Get reminders for specific list"""
    reminders = reminders_table.search(Query().list_name == list_name)
    return ReminderList(name=list_name, reminders=reminders)

@app.post("/api/login/")
async def login(username: str, password: str):
    """Authenticate user"""
    authenticate_user(username, password)
    return {"message": "Login successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)