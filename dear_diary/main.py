import datetime
import os
from typing import Optional

import parsedatetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dear_diary.core.config import origins
from dear_diary.core.database import EntryManager
from dear_diary.core.database.backend import GitBackend
from dear_diary.core.models import Entry, Message
from dear_diary.utils import module_path

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(module_path(), "static/")),
    name="static",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(os.path.join(module_path(), "templates"))
entry_manager_backend = GitBackend("entries")


@app.get("/", response_class=HTMLResponse)
def show_diary(request: Request, date: Optional[str] = None):
    if not date:
        date = str(datetime.date.today())

    try:
        date_parsed = datetime.date.fromisoformat(date)

        if date_parsed > datetime.date.today():
            raise ValueError("Date cannot be in the future")
    except ValueError:
        # FIXME: should probably return an error message to the user
        return RedirectResponse(url="/", status_code=302)

    with EntryManager(entry_manager_backend) as entry_manager:
        # get the index of the current entry in the sorted entries
        if entry := entry_manager.get_entry(date_parsed):
            entry_number = sorted(entry_manager.entries).index(entry) + 1
        else:
            entry_number = len(entry_manager.entries) + 1

        context = {
            "relevant_entries": list(
                map(lambda single_entry: single_entry.date, entry_manager.entries[:5])
            ),
            "diary_entry_placeholder": f"Entry for {date_parsed}...",
            "date": date_parsed,
            "entry_number": entry_number,
        }
        return templates.TemplateResponse(request, "index.html", context)


@app.post(
    "/entry",
    response_model=Message,
    responses={
        400: {"model": Message, "description": "Invalid entry data."},
        200: {"model": Message, "description": "Entry successfully added."},
    },
)
def post_entry(entry: Entry):
    with EntryManager(entry_manager_backend) as entry_manager:
        entry_manager.add_entry(entry)

    return JSONResponse(
        content={
            "message": f"Entry successfully added for {entry.date}.",
        }
    )


@app.get(
    "/entry/{entry_date}",
    response_model=Entry,
    responses={
        404: {"model": Message, "description": "Entry not found."},
    },
)
def get_entry(entry_date: str):
    with EntryManager(entry_manager_backend) as entry_manager:
        entry = entry_manager.get_entry(datetime.date.fromisoformat(entry_date))
        if entry is None:
            return JSONResponse(
                status_code=404,
                content={"message": f"Entry for {entry_date} not found."},
            )
        return entry


@app.get(
    "/entry",
    response_model=list[Entry],
    responses={
        400: {"model": Message, "description": "Invalid query or search range."},
        422: {"model": Message, "description": "Query cannot be empty."},
    },
)
def search(query: str, search_range: int = 7):
    if not query or query == "":
        return JSONResponse(
            status_code=422,
            content={"message": "Query cannot be empty."},
        )

    cal = parsedatetime.Calendar()

    query_parsed, query_success = cal.parse(query)
    query_date = datetime.date(*query_parsed[:3])
    search_delta = datetime.timedelta(days=search_range)

    if query_success == 0:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Invalid query or search range. Please provide a valid date or date range."
            },
        )

    with EntryManager(entry_manager_backend) as entry_manager:
        entries = entry_manager.get_entries(
            query_date - search_delta, query_date + search_delta
        )
        return entries
