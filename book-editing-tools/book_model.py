"""Small internal model for books with or without parts.

Public tool requests and results remain JSON-compatible dictionaries.
"""
from __future__ import annotations

from dataclasses import dataclass


ArticleReference = int | str


@dataclass(frozen=True)
class Article:
    ordinal: int
    title: str
    date: str | None
    date_status: str | None

    @classmethod
    def from_inventory(cls, item: dict) -> Article:
        return cls(item["ordinal"], item["title"], item["date"], item["date_status"])

    def as_dict(self) -> dict:
        return {"ordinal": self.ordinal, "title": self.title,
                "date": self.date, "date_status": self.date_status}


@dataclass(frozen=True)
class Part:
    title: str
    references: tuple[ArticleReference, ...]


@dataclass(frozen=True)
class BookPlan:
    parts: tuple[Part, ...] | None = None
    articles: tuple[ArticleReference, ...] | None = None

    @classmethod
    def from_request(cls, *, parts: list[dict] | None = None,
                     articles: list[ArticleReference] | None = None) -> BookPlan:
        if (parts is None) == (articles is None):
            raise ValueError("Provide exactly one of parts or articles")
        if articles is not None:
            if not isinstance(articles, list) or not articles:
                raise ValueError("articles must be a non-empty list")
            return cls(articles=tuple(articles))
        if not isinstance(parts, list) or not parts:
            raise ValueError("parts must be a non-empty list")
        parsed = []
        for index, part in enumerate(parts, 1):
            if not isinstance(part, dict) or not isinstance(part.get("title"), str) or not part["title"].strip():
                raise ValueError(f"part {index} requires a non-empty title")
            refs = part.get("articles")
            if not isinstance(refs, list) or not refs:
                raise ValueError(f"part {index} requires a non-empty articles list")
            parsed.append(Part(part["title"].strip(), tuple(refs)))
        return cls(parts=tuple(parsed))

    @property
    def layout(self) -> str:
        return "parts" if self.parts is not None else "flat"

    def groups(self) -> tuple[Part, ...]:
        if self.parts is not None:
            return self.parts
        return (Part("", self.articles or ()),)
