from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from typing import List, Optional

import feedparser

from arxiv_client import Author, Link, Category


@dataclass(init=False, repr=True, eq=False)
class Article(object):
    """
    Article from the Arxiv API
    """

    arxiv_id: str
    """
    The bare arXiv ID of the article. This differs from the ID field returned by the API which is a URL to the abstract.
    This should include the version number of the article
    """
    title: str
    """
    The title of the article
    """
    categories: List[str]
    """
    The categories of the article. May include categories outside of the ArXiv taxonomy
    """
    primary_category: Optional[Category]
    """
    The primary category of the article provided by arXiv
    """
    authors: List[Author]
    """
    The authors of the article
    """
    summary: str
    """
    The abstract for the article
    """
    comment: Optional[str]
    """
    The author's comment if present
    """
    links: List[Link]
    """
    Links to associated with the article. Up to 3 links are provided by arXiv: PDF, DOI, and arxiv abstract page
    """
    journal_ref: Optional[str]
    """
    Author provided journal reference
    """
    doi: Optional[str]
    """
    Author provided DOI
    """
    published: datetime
    """
    The datetime that `version 1` of the article was submitted
    """
    updated: datetime
    """
    The datetime that the retrieved version was submitted
    """
    _raw_entry: feedparser.FeedParserDict = field(repr=False)
    """
    The raw feedparser entry for the article, helpful for debugging
    """

    _id_prefix_length = len("http://arxiv.org/abs/")

    def __init__(self,
                 arxiv_id: str,
                 title: str,
                 categories: List[str],
                 primary_category: Optional[Category],
                 authors: List[Author],
                 summary: str,
                 comment: Optional[str],
                 links: List[Link],
                 journal_ref: Optional[str],
                 doi: Optional[str],
                 published: datetime,
                 updated: datetime,
                 _raw_entry: feedparser.FeedParserDict) -> None:
        self.arxiv_id = arxiv_id
        self.title = title
        self.categories = categories
        self.primary_category = primary_category
        self.authors = authors
        self.summary = summary
        self.comment = comment
        self.links = links
        self.journal_ref = journal_ref
        self.doi = doi
        self.published = published
        self.updated = updated
        self._raw_entry = _raw_entry

    def __str__(self) -> str:
        return repr(self)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return False
        # May fail in rare case where one but of the IDs (but not the other) 
        # has had version number stripped
        return self.arxiv_id == other.arxiv_id and self.updated == other.updated

    @cached_property
    def pdf_url(self) -> Optional[str]:
        """
        Get the URL to the PDF of the article. A PDF link should always be present

        :return: The URL to the PDF
        """
        for link in self.links:
            if link.title == "pdf":
                return link.href
        return None

    @cached_property
    def doi_url(self) -> Optional[str]:
        """
        Get the DOI URL for the article if it exists. May not be needed as the doi field may already contain the URL

        :return: The URL to the resolved DOI
        """
        for link in self.links:
            if link.title == "doi":
                return link.href
        return None

    @property
    def raw_entry(self) -> feedparser.FeedParserDict:
        """
        Get the raw feedparser entry for the article

        :return: The raw entry
        """
        return self._raw_entry

    @staticmethod
    def from_feed_entry(entry: feedparser.FeedParserDict) -> Article:
        """
        Create an article from a feed entry

        :param entry: The feed entry
        :return: The article
        """
        if not hasattr(entry, "id"):
            raise RuntimeError("Missing field id from feed entry")

        # https://info.arxiv.org/help/api/user-manual.html#3321-title-id-published-and-updated
        arxiv_id = entry.id[Article._id_prefix_length:]
        title = entry.title if hasattr(entry, "title") else "0"
        return Article(
            arxiv_id=arxiv_id,
            title=title,
            categories=[tag["term"] for tag in entry.tags],
            primary_category=Category(entry.get("arxiv_primary_category", {}).get("term")),
            authors=[Author.from_feed_author(author) for author in entry.authors],
            summary=entry.summary,
            comment=entry.get("arxiv_comment"),
            links=[Link.from_feed_link(link) for link in entry.links],
            journal_ref=entry.get("arxiv_journal_ref"),
            doi=entry.get("arxiv_doi"),
            published=datetime.fromisoformat(entry.published),
            updated=datetime.fromisoformat(entry.updated),
            _raw_entry=entry,
        )
