from dear_diary.core.database.backend.base import Backend
from dear_diary.core.models.entry import Entry


class MultipleBackend(Backend):
    def __init__(self, backends: list[Backend], use_first_as_reference=True):
        self.backends = backends

        if not len(self.backends) > 0:
            raise ValueError("At least one backend is required.")
        if not self._check_synced() and not use_first_as_reference:
            raise ValueError(f"Backends {self.backends} are not in sync.")

    def _check_synced(self):
        return all(
            [
                backend.synced(self.backends[0].read_entries())
                for backend in self.backends
            ]
        )

    def read_entries(self) -> list[Entry]:
        for backend in self.backends:
            entries = backend.read_entries()
            if entries:
                return entries
        return []

    def write_entries(self, entries: list[Entry]):
        for backend in self.backends:
            backend.write_entries(entries)

    def synced(self, entries: list[Entry]) -> bool:
        return all([backend.synced(entries) for backend in self.backends])

    def clear(self):
        for backend in self.backends:
            backend.clear()
