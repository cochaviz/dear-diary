import datetime

# from flask import Flask, render_template, request, url_for, redirect
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from entries import Entry, EntryManager, GitBackend

# app = Flask(__name__)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates("templates")
entry_manager_backend = GitBackend("entries")

@app.get("/")
def home(request: Request):
    """
    Redirect to entry of the current day.
    """
    return RedirectResponse(url=f"/{datetime.date.today()}", status_code=302)

@app.get("/{entry_date}", response_class=HTMLResponse)
def index(entry_date: str, request: Request):
    try:
        date = datetime.date.fromisoformat(entry_date) 
        if date > datetime.date.today():
            raise ValueError("Date cannot be in the future")
    except ValueError:
        # FIXME: should probably return an error message to the user
        return RedirectResponse(url="/", status_code=302)

    with EntryManager(entry_manager_backend) as entry_manager:
        # get the index of the current entry in the sorted entries
        if (entry := entry_manager.get_entry(date)):
            entry_number = sorted(entry_manager.entries).index(entry) + 1
        else:
            entry_number = len(entry_manager.entries) + 1

        context = {
            "relevant_entries" : list(map(
                lambda single_entry: single_entry.date, 
                entry_manager.entries[:5]
            )),
            "diary_entry_placeholder" : f"Entry for {date}...",
            "date" : date,
            "entry_number" : entry_number,
        }
        return templates.TemplateResponse(request, "index.html", context)

@app.post("/entry/")
def post_entry(entry: Entry):
    """
    Get (GET) or add (POST) an entry for a specific date. Format of date is
    YYYY-MM-DD, and the entry is expected to be in JSON format where the key
    is "entry" and the value is the content of the entry.

    Status codes:
        400: Entry is empty or not provided.
        404: Entry not found.
        405: Invalid request.
    """
    with EntryManager(entry_manager_backend) as entry_manager:
        entry_manager.add_entry(entry)

    return { 
        "message": f"Entry for added for {entry.date} was successfully added!", 
    }


@app.get("/entry/{entry_date}")
def get_entry(entry_date: str):
    with EntryManager(entry_manager_backend) as entry_manager:
        entry = entry_manager.get_entry(datetime.date.fromisoformat(entry_date))
        if entry is None:
            return { "error": "Entry not found" }, 404
        return entry

