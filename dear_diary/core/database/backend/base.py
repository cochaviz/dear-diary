from abc import ABC, abstractmethod
from typing import Optional

from dear_diary.core.models.entry import Entry


class DatabaseBackend(ABC):
    @abstractmethod
    def read_entries(self) -> list[Entry]:
        """
        Reads the entries from the backend and returns them as a list.
        """
        raise NotImplementedError()

    @abstractmethod
    def write_entries(self, entries: list[Entry]):
        """
        Writes the entries to the backend.

        The backend should be able to handle the case when the entries are
        empty.
        """
        raise NotImplementedError()

    @abstractmethod
    def synced(self, entries: list[Entry]) -> bool:
        """
        Returns True if the backend is in sync with the local entries.

        The backend is considered to be in sync if the entries in the
        backend are the same as the entries in the list. The order of
        the entries is not important.
        """
        raise NotImplementedError()

    @abstractmethod
    def clear(self):
        """
        Clears the backend of all entries.

        Ensure that this operation is not destructive.
        """
        raise NotImplementedError()

    def last_update_time(self) -> Optional[float]:
        """
        Returns the time of the last update to the backend.

        The time should be in seconds since the epoch.

        Returns None if the database has uncommitted changes.
        """
        raise NotImplementedError()
