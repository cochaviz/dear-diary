import datetime

from dear_diary.core.database.backend.base import Backend
from dear_diary.core.models.entry import Entry


class EntryManager:
    def __init__(self, backend: Backend):
        self.entries: list[Entry] = []
        self.backend: Backend = backend

    def add_entry(self, entry: Entry):
        self.entries.append(entry)
        self.entries.sort()

    def get_entry(self, date: datetime.date):
        for entry in self.entries:
            if entry.date == date:
                return entry
        return None

    def get_entries(self, start_date: datetime.date, end_date: datetime.date):
        return [entry for entry in self.entries if start_date <= entry.date <= end_date]

    def __enter__(self):
        self.entries = self.backend.read_entries()
        return self

    def __exit__(self, *_):
        self.backend.write_entries(self.entries)
