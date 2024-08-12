import datetime

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# local imports
from dear_diary.core.models import Entry, Message
from dear_diary.core.database import EntryManager, GitBackend

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates("templates")
entry_manager_backend = GitBackend("entries")

@app.get("/")
def show_diary_today(request: Request):
    """
    Redirect to entry of the current day.
    """
    return show_diary(str(datetime.date.today()), request)

@app.get("/{entry_date}", response_class=HTMLResponse)
def show_diary(entry_date: str, request: Request):
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

@app.post(
    "/entry/",
    response_model=Message,
)
def post_entry(entry: Entry):
    with EntryManager(entry_manager_backend) as entry_manager:
        entry_manager.add_entry(entry)
        print(entry_manager.entries)

    return JSONResponse(content={
        "message": f"Entry for added for {entry.date} was successfully added!", 
    })


@app.get(
    "/entry/{entry_date}",
    response_model=Entry,
    responses= {
        404: { "model": Message, "description": "Entry not found." },
    }
)
def get_entry(entry_date: str):
    with EntryManager(entry_manager_backend) as entry_manager:
        entry = entry_manager.get_entry(datetime.date.fromisoformat(entry_date))
        if entry is None:
            return JSONResponse(
                status_code=404, 
                content={ "message": f"Entry for {entry_date} not found." }
            )
        return entry


