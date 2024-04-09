# arxiv-client

Python3 client for the [arXiv API](https://info.arxiv.org/help/api/user-manual.html).
Install package from [PyPI](https://pypi.org/project/arxiv-client/): `arxiv_client`.

This differs from the pre-existing [arxiv.py](https://github.com/lukasschwab/arxiv.py) project 
in that it further abstracts away the arXiv API so you do not need to learn to construct
query strings. The overall goal is to enable users to skip reading the API docs entirely.

`arxiv.py` is currently:

- More stable
- Compatible with Python < 3.11
- Performant for large queries

## Basic Features

- Simple query building
- Comprehensive entity models, with documentation
  - For example, see the [Category](src/arxiv_client/category.py) enum for arXiv's subject taxonomy
- Fully type annotated

### Under Development

- Improved page chunking for large queries
- Support for querying more fields
- Testing and validation

## Usage

In a nutshell:

```py
import arxiv_client as arx
import pprint

categories = [arx.Category.CS_AI, arx.Category.CS_CL, arx.Category.CS_IR]
client = arx.Client()
articles = client.search(arx.Query(keywords=["llm"], categories=categories, max_results=2))
for article in articles:
  pprint.pprint(article)  # Formatted pretty print is supported
```

### Structured Query Logic

When using the structured `Query` fields, multiple values within a single field are combined using `OR`, 
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

See the [Query](src/arxiv_client/query.py) class for more information.

### Custom Queries

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

This uses [hatch](https://hatch.pypa.io/latest/) for project management.
