from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import feedparser


@dataclass(init=False, repr=True, eq=False)
class Author(object):
    """
    Author of an article
    """

    name: str
    """
    Full name of the author
    """
    affiliation: Optional[str]
    """
    The affiliation of the author. This is rarely populated
    """

    def __init__(self, name: str, affiliation: Optional[str] = None) -> None:
        self.name = name
        self.affiliation = affiliation

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_feed_author(author: feedparser.FeedParserDict) -> Author:
        """
        Create an Author object from a feedparser author entry

        :param author: The feedparser author entry
        :return: The Author object
        """
        name = author.get("name")
        affiliation = author.get("arxiv_affiliation")
        return Author(name, affiliation)
