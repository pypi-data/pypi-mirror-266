from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import feedparser


@dataclass(init=False, repr=True, eq=False)
class Link(object):
    """
    Link to an article
    """

    title: Optional[str]
    """
    The title of the link
    """
    href: str
    """
    The URL of the link
    """
    rel: Optional[str]
    """
    The relation of the link. Can be alternate or related
    """
    type: Optional[str]
    """
    MIME type of the entity being linked, e.g., text/html
    """

    def __init__(self, title: Optional[str], href: str, rel: Optional[str], mime_type: Optional[str]) -> None:
        self.title = title
        self.href = href
        self.rel = rel
        self.type = mime_type

    def __str__(self) -> str:
        return self.href

    @staticmethod
    def from_feed_link(link: feedparser.FeedParserDict) -> Link:
        """
        Create a Link object from a feedparser link entry

        :param link: The feedparser link entry
        :return: The Link object
        """
        title = link.get("title")
        href = link["href"]
        rel = link.get("rel")
        mime_type = link.get("type")
        return Link(title, href, rel, mime_type)
