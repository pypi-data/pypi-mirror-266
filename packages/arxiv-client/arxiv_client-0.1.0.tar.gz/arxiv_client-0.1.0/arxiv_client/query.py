from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any

from arxiv_client import Category


class SortBy(Enum):
    """
    Sort criterion for the query results

    See [the arXiv API User's Manual: sort order for return
    results](https://arxiv.org/help/api/user-manual#sort).
    """
    RELEVANCE = "relevance"
    LAST_UPDATED_DATE = "lastUpdatedDate"
    SUBMITTED_DATE = "submittedDate"


class SortOrder(Enum):
    """
    Sort order of the query results

    See [the arXiv API User's Manual: sort order for return
    results](https://arxiv.org/help/api/user-manual#sort).
    """
    ASC = "ascending"
    DESC = "descending"


@dataclass(init=False, repr=True)
class SortCriterion(object):
    """
    Sort criterion for the query results
    """
    sort_by: SortBy
    """
    Sort by
    """
    sort_order: SortOrder
    """
    Sort order
    """

    def __init__(self, sort_by: SortBy = SortBy.LAST_UPDATED_DATE, sort_order: SortOrder = SortOrder.DESC) -> None:
        """
        :param sort_by: The criterion to sort by
        :param sort_order: The order to sort by
        """
        self.sort_by = sort_by
        self.sort_order = sort_order


class Field(Enum):
    """
    Searchable fields and their corresponding prefix used in query string construction

    See [Arxiv Query Construction](https://info.arxiv.org/help/api/user-manual.html#query_details)
    """
    TITLE = "ti"
    AUTHOR = "au"
    ABSTRACT = "abs"
    COMMENT = "co"
    JOURNAL_REFERENCE = "jr"
    CATEGORY = "cat"
    REPORT_NUMBER = "rn"
    ID = "id"  # DEPRECATED: use `id_list` instead. Using this field will not handle article versions properly
    ALL = "all"


@dataclass(init=False, repr=True, eq=False)
class Query(object):
    """
    Typed wrapper for an Arxiv query. Multiples values within a single field are combined with `OR`,
    while multiple fields are combined with `AND`.

    For more advanced query logic, use the `custom_params` field to pass in a raw query string.

    See [Arxiv Query Interface](https://info.arxiv.org/help/api/user-manual.html#311-query-interface)
    [Arxiv Query Construction](https://info.arxiv.org/help/api/user-manual.html#query_details)
    """
    # TODO: Support for remaining searchable fields
    #   - abstract
    #   - comment
    #   - journal reference
    #   - report number
    keywords: List[str]
    """
    Keywords to search across all fields.
    """
    title_keywords: List[str]
    """
    Title keywords to filter on.
    """
    author_names: List[str]
    """
    Author names to filter on.
    """
    categories: List[Category]
    """
    Subject categories to filter on.
    """
    article_ids: List[str]
    """
    ArXiv article IDs to filter on.
    """
    custom_params: Optional[str]
    """
    Query param string for advanced users. This is helpful if query logic is not supported, e.g.,
    searching by `AND` logic between keywords.
    """
    sort_criterion: Optional[SortCriterion]
    """
    SortBy and SortOrder for the query results. Default is to sort by LAST_UPDATED_DATE in DESC order
    Pass `None` to use API default sort
    """
    start: Optional[int]
    """
    Pagination parameter using zero-based indexing
    """
    max_results: Optional[int]
    """
    The max number of results to get. Set to `None` to get maximum number of results allowed by the API.
    Requests with `max_results` set >30_000 will result in HTTP 400 error
    """

    def __init__(self,
                 keywords: Optional[List[str]] = None,
                 title_keywords: Optional[List[str]] = None,
                 author_names: Optional[List[str]] = None,
                 categories: Optional[List[Category]] = None,
                 article_ids: Optional[List[str]] = None,
                 custom_params: Optional[str] = None,
                 sort_criterion: Optional[SortCriterion] = SortCriterion(),
                 start: Optional[int] = None,
                 max_results: Optional[int] = 10) -> None:
        """
        :param keywords: Keywords to search across all fields
        :param title_keywords: Title keywords to filter on
        :param author_names: Author names to filter on
        :param categories: Categories to filter on
        :param article_ids: ArXiv article IDs to filter on. If you want to retrieve a specific version, simply append
            `v{version#}` to the article ID, e.g., `2103.12345v1` for version 1 of article `2103.12345`
        :param custom_params: Raw query string for advanced users
        :param sort_criterion: Sort criterion for the query results
        :param max_results: The max number of results to get
        """
        self.keywords = [] if keywords is None else keywords
        self.title_keywords = [] if title_keywords is None else title_keywords
        self.author_names = [] if author_names is None else author_names
        self.categories = [] if categories is None else categories
        self.article_ids = [] if article_ids is None else article_ids
        self.custom_params = custom_params
        self.sort_criterion = sort_criterion
        self.start = start
        self.max_results = max_results

    def __str__(self) -> str:
        return repr(self)

    def _to_url_params(self) -> Dict[str, Any]:
        """
        Construct the full query as a Dict of query parameters, not yet URL encoded.

        See [Arxiv Query Construction](https://info.arxiv.org/help/api/user-manual.html#query_details)
        :return: The URL parameters
        """
        keywords = " OR ".join(f"{Field.ALL.value}:\"{keyword}\"" for keyword in self.keywords) if self.keywords else ""
        title_keywords = " OR ".join(f"{Field.TITLE.value}:\"{keyword}\"" for keyword in self.title_keywords) \
            if self.title_keywords else ""
        authors = " OR ".join([f"{Field.AUTHOR.value}:\"{author}\"" for author in self.author_names]) \
            if self.author_names else ""
        categories = " OR ".join([f"{Field.CATEGORY.value}:{category.value}" for category in self.categories]) \
            if self.categories else ""

        partials: List[str] = []
        if keywords:
            partials.append(f"({keywords})")
        if title_keywords:
            partials.append(f"({title_keywords})")
        if authors:
            partials.append(f"({authors})")
        if categories:
            partials.append(f"({categories})")
        if self.custom_params:
            partials.append(f"({self.custom_params})")

        return {
            "search_query": " AND ".join(partials),
            "id_list": ",".join(self.article_ids),
            **({"sortBy": self.sort_criterion.sort_by.value, "sortOrder": self.sort_criterion.sort_order.value}
               if self.sort_criterion is not None else {}),
            **({"max_results": self.max_results} if self.max_results is not None else {}),
            **({"start": self.start} if self.start is not None else {})
        }
