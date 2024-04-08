import logging
from typing import List

import feedparser
import requests

from arxiv_client import Article, Query

logger = logging.getLogger(__name__)


class Client(object):
    """
    Python wrapper for the Arxiv API
    """

    base_search_url = "https://export.arxiv.org/api/query"
    """
    Base URL for Arxiv API
    """

    _session = requests.Session()

    def __init__(self) -> None:
        self._session.headers.update({"User-Agent": "arxiv-client-py"})

    # TODO:
    #  1. Generator
    #  2. Advanced paging
    #  3. Consider async io
    def search(self, query: Query) -> List[Article]:
        """
        Search the Arxiv API

        :param query: The query to search with
        :return: The search results
        """
        logger.debug(f"Searching arxiv with query: {query}")
        response = self._session.get(self.base_search_url, params=query._to_url_params())
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        logger.debug(f"ArXiv returned {len(feed.entries)} results")
        return [Article.from_feed_entry(entry) for entry in feed.entries]
