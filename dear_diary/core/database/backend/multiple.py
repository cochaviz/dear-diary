from dear_diary.core.database.backend.base import DatabaseBackend
from dear_diary.core.models.entry import Entry


class MultipleBackend(DatabaseBackend):
    def __init__(
        self,
        backends: set[DatabaseBackend],
        # FIXME: would be nice if this was optional
        reference: DatabaseBackend,
    ):
        self.backends: set[DatabaseBackend] = backends
        self.reference: DatabaseBackend = reference

        assert not reference or reference in backends

        if not len(self.backends) > 0:
            raise ValueError("At least one backend is required.")
        if not self._check_synced():
            raise ValueError(f"Backends {self.backends} are not in sync.")

    def _check_synced(self):
        reference_entries = self.reference.read_entries()

        return all(
            [
                backend.synced(reference_entries)
                for backend in self.backends
                if backend != self.reference  # don't compare the reference to itself
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
