"""
Bulldoggy Reminders App - Simplified Implementation
Source: AutomationPanda/bulldoggy-reminders-app (GitHub)
Date: 2023-11-20
Description: A minimal FastAPI implementation of Bulldoggy reminders app with TinyDB backend.
Includes login, reminder list CRUD operations, and basic HTML interface using HTMX.
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from pydantic import BaseModel
from tinydb import TinyDB, Query
import secrets
from pathlib import Path

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Database setup
db_path = Path("reminder_db.json")
db = TinyDB(db_path)
reminder_lists = db.table("reminder_lists")

# Configuration (simplified from config.json)
USERS = {
    "pythonista": {"password": "I<3testing", "token": "demo_token"}
}

class Reminder(BaseModel):
    text: str
    completed: bool = False

class ReminderList(BaseModel):
    name: str
    reminders: List[Reminder] = []

def authenticate_user(username: str, password: str) -> Optional[str]:
    """Check credentials and return session token if valid"""
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]["token"]
    return None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str, password: str):
    """Handle login form submission"""
    token = authenticate_user(username, password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    response = RedirectResponse(url="/reminders", status_code=303)
    response.set_cookie(key="session_token", value=token)
    return response

@app.get("/reminders", response_class=HTMLResponse)
async def reminders_page(request: Request):
    """Render main reminders interface"""
    # In a real app, validate session token first
    lists = reminder_lists.all()
    return templates.TemplateResponse(
        "reminders.html",
        {"request": request, "lists": lists}
    )

@app.post("/api/lists")
async def create_list(list_data: ReminderList):
    """API endpoint to create new reminder list"""
    reminder_lists.insert(list_data.dict())
    return {"status": "success"}

@app.get("/api/lists/{list_id}", response_model=ReminderList)
async def get_list(list_id: int):
    """API endpoint to get a specific reminder list"""
    list_data = reminder_lists.get(doc_id=list_id)
    if not list_data:
        raise HTTPException(status_code=404, detail="List not found")
    return list_data

@app.delete("/api/lists/{list_id}")
async def delete_list(list_id: int):
    """API endpoint to delete a reminder list"""
    reminder_lists.remove(doc_ids=[list_id])
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)