from dataclasses import dataclass
from typing import Self

import feedparser  # type: ignore


@dataclass(init=True, repr=True, eq=True)
class Link:
    """
    Link to an article
    """

    title: str | None
    """
    The title of the link
    """
    href: str
    """
    The URL of the link
    """
    rel: str | None
    """
    The relation of the link. Can be alternate or related
    """
    mime_type: str | None
    """
    MIME type of the entity being linked, e.g., text/html
    """

    def __str__(self) -> str:
        return self.href

    @classmethod
    def from_feed_link(cls, link: feedparser.FeedParserDict) -> Self:
        """
        Create a Link object from a feedparser link entry

        :param link: The feedparser link entry
        :return: The Link object
        """
        title = link.get("title")
        href = link["href"]
        rel = link.get("rel")
        mime_type = link.get("type")
        return cls(title, href, rel, mime_type)
