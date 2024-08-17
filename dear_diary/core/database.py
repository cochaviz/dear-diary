import datetime
import glob
import os
from abc import ABC, abstractmethod

import frontmatter
from git import InvalidGitRepositoryError, NoSuchPathError, Repo

from dear_diary.core.models.entry import Entry


class Backend(ABC):
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


class GitBackend(Backend):
    """
    Manages entries using a git repository as the backend. The repository
    is assumed to be a local repository.

    The entries are saved as markdown files in the repository in the
    top-level directory. Each file is named after the date of the entry and
    the 'metadata' is saved as the 'frontmatter' of the markdown file.
    """

    repo: Repo = None  # type: ignore

    def __init__(self, repo_path, init_if_not_exists=True):
        try:
            self.repo = Repo(repo_path)
        except NoSuchPathError or InvalidGitRepositoryError:
            if init_if_not_exists:
                self._init_repo(repo_path)

        assert (
            self.repo and not self.repo.bare
        ), f"Repository at {repo_path} is faulty or does not exist. Make sure `init_if_not_exists` is set to True."

    def _init_repo(self, repo_path):
        if os.path.exists(repo_path):
            if os.path.isdir(repo_path) and os.listdir(repo_path):
                raise ValueError(f"Directory {repo_path} is not empty.")
            if not os.path.isdir(repo_path):
                raise ValueError(f"Path {repo_path} is not a directory.")
            # otherwise, it's safe to remove the directory
            # FIXME: this is a bit dangerous, perhaps just rename the directory
            os.rmdir(repo_path)

        self.repo = Repo.init(repo_path)

    def _markdown_files_in(self, folder_path: str):
        return glob.glob(os.path.join(folder_path, "*.md"))

    def _read_entries_from_path(self, folder_path: str):
        entries = []

        for markdown_file in self._markdown_files_in(folder_path):
            with open(markdown_file, "r") as file:
                date = os.path.basename(markdown_file).replace(".md", "")
                file = frontmatter.load(file)
                try:
                    entries.append(
                        Entry(
                            # I might regret this formatting later
                            date=datetime.date.fromisoformat(date),
                            content=file.content,
                            metadata=file.metadata,
                        )
                    )
                except ValueError:
                    print(
                        f"Pydantic validation failed for entry. Please check entry {date}."
                    )
        return entries

    def _write_entries_to_path(self, folder_path: str, entries: list[Entry]):
        for entry in entries:
            with open(os.path.join(folder_path, f"{entry.date}.md"), "w") as file:
                file_content = entry.content

                # handle presence of metadata
                if len(entry.metadata) > 0:
                    file_content = frontmatter.dumps(
                        frontmatter.Post(entry.content, **entry.metadata)
                    )
                file.write(file_content)

    def read_entries(self) -> list[Entry]:
        return self._read_entries_from_path(str(self.repo.working_dir))

    def write_entries(self, entries: list[Entry]):
        self._write_entries_to_path(str(self.repo.working_dir), entries)
        self.repo.index.add(self._markdown_files_in(str(self.repo.working_dir)))
        self.repo.index.commit("Update entries")

    def synced(self, entries: list[Entry]) -> bool:
        return (
            entries == self.read_entries() and not self.repo.is_dirty()
        )  # necessary to check for untracked files

    def clear(self):
        """
        Technically clears the repository, but just moves the folder to a
        different name (<folder>_bak). This is to prevent accidental data
        loss.
        """
        os.rename(str(self.repo.working_dir), f"{str(self.repo.working_dir)}_bak")


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
