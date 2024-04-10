from dataclasses import dataclass
from typing import Self

import feedparser  # type: ignore


@dataclass(init=False, repr=True, eq=False)
class Author:
    """
    Author of an article
    """

    name: str
    """
    Full name of the author
    """
    affiliation: str | None
    """
    The affiliation of the author. This is rarely populated
    """

    def __init__(self, name: str, affiliation: str | None = None) -> None:
        self.name = name
        self.affiliation = affiliation

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_feed_author(cls, author: feedparser.FeedParserDict) -> Self:
        """
        Create an Author object from a feedparser author entry

        :param author: The feedparser author entry
        :return: The Author object
        """
        name = author.get("name")
        affiliation = author.get("arxiv_affiliation")
        return cls(name, affiliation)
