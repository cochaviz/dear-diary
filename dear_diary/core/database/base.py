import datetime

from dear_diary.core.database.backend.base import DatabaseBackend
from dear_diary.core.models.entry import Entry


class EntryManager:
    def __init__(self, backend: DatabaseBackend):
        self.entries: list[Entry] = []
        self.backend: DatabaseBackend = backend

    def add_entry(self, entry: Entry):
        """
        Add an entry to the database.
        """
        self.entries.append(entry)
        self.entries.sort()

    def get_entry(self, date: datetime.date):
        """
        Get an entry by date.
        """
        for entry in self.entries:
            if entry.date == date:
                return entry
        return None

    def get_entries(self, start_date: datetime.date, end_date: datetime.date):
        """
        Get all entries between two dates.
        """
        return [entry for entry in self.entries if start_date <= entry.date <= end_date]

    def get_info(self):
        """
        Get information about the database.
        """
        return {
            "last_time": self.backend.last_update_time(),
        }

    def __enter__(self):
        self.entries = self.backend.read_entries()
        return self

    def __exit__(self, *_):
        self.backend.write_entries(self.entries)
