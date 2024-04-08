# arxiv-client

Python3 client for the [arXiv API](https://info.arxiv.org/help/api/user-manual.html).

This differs from the pre-existing [arxiv.py](https://github.com/lukasschwab/arxiv.py) project 
in that it further abstracts away the arXiv API so you do not need to learn to build query 
strings on your own.

The overall goal is to enable most users to query arXiv immediately, without needing to 
reference the API docs.

`arxiv.py` is currently more stable and is backwards compatible with older versions of Python.
It is also currently recommended for queries that return large numbers of results.

## Basic Features

- Simple query building
- Comprehensive entity models, with documentation
  - For example, see the [Category](./arxiv_client/category.py) enum for arXiv's subject taxonomy
- Fully type annotated

### Under Development

- Improved page chunking for large queries
- Support for querying more fields
- Testing and validation

## Usage

In a nutshell:

```py
from arxiv_client import Client, Query, Category
import pprint


categories = [Category.CS_AI, Category.CS_CL, Category.CS_IR]
client = Client()
articles = client.search(Query(keywords=["llm"], categories=categories, max_results=2))
for article in articles:
    pprint.pprint(article) # Formatted pretty print is supported
```

### Simple Query Logic

When using the provided `Query` fields, multiple values within a single field are combined using `OR`, 
and multiple fields are combined using `AND`.

#### Example

```py
Query(keywords=["llm"], categories=[Category.CS_AI, Category.CS_IR], max_results=5)
# Query(keywords=['llm'],
#       title_keywords=[],
#       author_names=[],
#       categories=[<Category.CS_AI: 'cs.AI'>, <Category.CS_IR: 'cs.IR'>],
#       article_ids=[],
#       custom_params=None,
#       sort_criterion=SortCriterion(sort_by=<SortBy.LAST_UPDATED_DATE: 'lastUpdatedDate'>,
#                                    sort_order=<SortOrder.DESC: 'descending'>),
#       start=None,
#       max_results=5)
```

Results in the following query logic:

```
(all:"llm") AND (cat:cs.AI OR cat:cs.IR)
```

See the [Query](./arxiv_client/query.py) class for more information.

### Advanced Query Logic

If the provided simple query logic is insufficient, the `Query` object takes a self-built query string through the `custom_params` attribute. You do not need to URL encode this value.

See [arXiv Query Construction](https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction) for more information on building your own queries.

#### Example

```py
custom = f"cat:{Category.CS_AI.value} ANDNOT cat:{Category.CS_RO.value}"
Query(keywords=["paged attention", "attention window"], custom_params=custom)
# Query(keywords=['paged attention', 'attention window'],
#       title_keywords=[],
#       author_names=[],
#       categories=[],
#       article_ids=[],
#       custom_params='cat:cs.AI ANDNOT cat:cs.RO',
#       sort_criterion=SortCriterion(sort_by=<SortBy.LAST_UPDATED_DATE: 'lastUpdatedDate'>,
#                                    sort_order=<SortOrder.DESC: 'descending'>),
#       start=None,
#       max_results=10)
```

Results in the following query logic:

```
(all:"paged attention" OR all:"attention window") AND (cat:cs.AI ANDNOT cat:cs.RO)
```

## Development

### Getting Started

This uses [poetry](https://python-poetry.org/) for dependency management.
See the [poetry documentation](https://python-poetry.org/docs) for usage.

In a nutshell:

1. Install [poetry](https://python-poetry.org/)
2. Install project dependencies
   
    ```shell
    poetry install
    ```
3. Activate compatible virtual environment

    ```shell
    poetry shell
    ```

### Contributing

A goal was to aid in learning modern Python practices. 
PRs and comments for improving style or best practice are appreciated.
