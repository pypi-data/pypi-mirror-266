import copy
import logging
import time
from collections.abc import Iterator
from datetime import datetime, timedelta

import feedparser  # type: ignore
import requests

from arxiv_client import Article, Query

logger = logging.getLogger(__name__)


class Client:
    """
    Python wrapper for the Arxiv API
    """

    base_search_url = "https://export.arxiv.org/api/query"
    """
    Base URL for Arxiv API
    """

    _session: requests.Session
    _last_request_dt: datetime | None

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "arxiv-client-py"})
        self._last_request_dt = None

    # TODO: Consider async io
    def search(
        self,
        query: Query,
        chunk_size: int | None = None,
        chunk_delay_ms: int = 1_000,
        chunk_max_retries: int = 1,
    ) -> Iterator[Article]:
        """
        Search the Arxiv API.

        The chunking parameters allow for the search to be broken up into smaller queries.
        This is useful for large queries, which allows you to process the results as a stream.
        In cases of failure, you can resume from last successful article processed by using
        the start parameter in the Query object.

        :param query: The query to search with
        :param chunk_size: The number of results to get in each chunk. None will fetch all results in one chunk
        :param chunk_delay_ms: The delay in milliseconds between each chunk request
        :param chunk_max_retries: The max number of retries for each chunk request
        :return: The search results
        """
        logger.debug("Searching arXiv with query: %r", query)
        subquery = copy.deepcopy(query)
        if chunk_size is not None:
            subquery.max_results = chunk_size

        total_retrieved = 0
        while total_retrieved < query.max_results:
            feed = self._get_search_chunk(subquery, chunk_delay_ms, chunk_max_retries)
            total_retrieved += len(feed.entries)
            total_results = int(feed.feed.opensearch_totalresults)

            logger.debug("Retrieved %d of %d total articles", total_retrieved, total_results)
            if not feed.entries:
                return

            for entry in feed.entries:
                yield Article.from_feed_entry(entry)

            if chunk_size is not None:
                subquery.start += chunk_size

    def _get_search_chunk(self, query: Query, chunk_delay_ms, chunk_max_retries: int) -> feedparser.FeedParserDict:
        """
        Get a chunk of search results from the Arxiv API

        :param query: The query to search with
        :param chunk_delay_ms: The delay in milliseconds between each chunk request
        :param chunk_max_retries: The max number of retries for each chunk request
        :return: The search results
        """
        try_count = 0
        while try_count <= chunk_max_retries:
            try:
                self._apply_chunk_delay(chunk_delay_ms)
                response = self._session.get(self.base_search_url, params=query._to_url_params())
                response.raise_for_status()
                self._last_request_dt = datetime.now()

                feed = feedparser.parse(response.content)
                logger.debug("Successfully retrieved chunk of %d articles", len(feed.entries))
                return feed
            except (requests.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
                logger.warning("Failed to retrieve chunk of articles: %s", e)
                try_count += 1

        msg = f"Failed to retrieve chunk of articles after {chunk_max_retries} retries"
        logger.error(msg, extra={"query": query})
        raise RuntimeError(msg)

    def _apply_chunk_delay(self, delay_ms: int) -> None:
        """
        Ensure a minimum delay of delay_ms since the last request. This is to avoid violating arXiv rate limit
        while fetching results in chunks.
        """
        if self._last_request_dt is None:
            return

        min_delay = timedelta(milliseconds=delay_ms)
        elapsed = datetime.now() - self._last_request_dt
        if elapsed < min_delay:
            wait_time = (min_delay - elapsed).total_seconds()
            logger.debug("Waiting %s seconds before next request", wait_time)
            time.sleep(wait_time)
