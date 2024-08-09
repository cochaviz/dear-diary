import datetime

from flask import Flask, render_template, request, url_for, redirect

from entries import Entry, EntryManager, GitBackend

app = Flask(__name__)
entry_manager_backend = GitBackend("entries")


@app.route("/", defaults={"entry_date": str(datetime.date.today())})
@app.route("/<entry_date>")
def index(entry_date: str):
    if request.method == "GET":
        try:
            date = datetime.date.fromisoformat(entry_date) 
            if date > datetime.date.today():
                raise ValueError("Date cannot be in the future")
        except ValueError:
            # FIXME: should probably return an error message to the user
            return redirect(url_for("index"))

        with EntryManager(entry_manager_backend) as entry_manager:
            # get the index of the current entry in the sorted entries
            if (entry := entry_manager.get_entry(date)):
                entry_number = sorted(entry_manager.entries).index(entry) + 1
            else:
                entry_number = len(entry_manager.entries) + 1

            return render_template( "index.html",
                # get 5 random entries
                relevant_entries= list(map(
                    lambda single_entry: single_entry.date, 
                    entry_manager.entries[:5]
                )),
                diary_entry_placeholder=f"Entry for {date}...",
                date=date,
                entry_number=entry_number,
            )

    return { "error": "Invalid request" }, 405




@app.route("/entry/<entry_date>", methods=["POST", "GET"])
def entry(entry_date):
    """
    Get (GET) or add (POST) an entry for a specific date. Format of date is
    YYYY-MM-DD, and the entry is expected to be in JSON format where the key
    is "entry" and the value is the content of the entry.

    Status codes:
        400: Entry is empty or not provided.
        404: Entry not found.
        405: Invalid request.
    """
    if request.method == "POST":
        if not request.json or "entry" not in request.json or not request.json["entry"]:
            return { "error" : "Please provide a non-empty entry." }, 400

        with EntryManager(entry_manager_backend) as entry_manager:
            entry_manager.add_entry(
                Entry(datetime.date.fromisoformat(entry_date), request.json["entry"])
            )

        return { 
            "message": f"Entry for added for {entry_date} was successfully added!", 
        }
    if request.method == "GET":
        with EntryManager(entry_manager_backend) as entry_manager:
            entry = entry_manager.get_entry(datetime.date.fromisoformat(entry_date))
            if entry is None:
                return { "error": "Entry not found" }, 404
            return { "entry": entry.content }

    return { "error": "Invalid request" }, 405




if __name__ == "__main__":
    app.run()
