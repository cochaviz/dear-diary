import datetime

from pydantic import BaseModel, field_validator


class Entry(BaseModel):
    date: datetime.date
    content: str
    metadata: dict = {}

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v):
        if v == "":
            raise ValueError("Content is not allowed to be empty.")
        return v

    def __repr__(self):
        return f"Entry(date={self.date}, entry={self.content})"

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return False
        return self.date == other.date and self.content == other.content

    def __hash__(self):
        return hash((self.date, self.content))

    def __lt__(self, other):
        if not isinstance(other, Entry):
            return NotImplemented
        return self.date < other.date

    def __le__(self, other):
        if not isinstance(other, Entry):
            return NotImplemented
        return self.date <= other.date

    def __gt__(self, other):
        if not isinstance(other, Entry):
            return NotImplemented
        return self.date > other.date

    def __ge__(self, other):
        if not isinstance(other, Entry):
            return NotImplemented
        return self.date >= other.date

    def __ne__(self, other):
        if not isinstance(other, Entry):
            return NotImplemented
        return self.date != other.date

    def __str__(self):
        return f"{self.date}: {self.content}"
