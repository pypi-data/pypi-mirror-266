from typing import Literal

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.news import (
    SearchResponse
)
from typing import Annotated

class NewsAPI(BaseAPI):
    """
    News API

    https://api.asknews.app/docs#tag/news
    """
    async def search_news(
        self,
        query: Annotated[
            str,
            "Query string that can be any phrase, "
            "keyword, question, or paragraph. "
            "If method='nl', then this will be used "
            "as a natural language query. If method='kw', "
            "then this will be used as a direct keyword query."
        ],
        n_articles: Annotated[int, "Number of articles to return"] = 10,
        start_timestamp: Annotated[
            int | None,
            "Start timestamp to search from"
        ] = None,
        end_timestamp: Annotated[int | None, "End timestamp to search to"] = None,
        return_type: Annotated[
            Literal["string", "dicts", "both"],
            "Type of return value. 'string' means "
            "that the return is prompt-optimized "
            "and ready to be immediately injected "
            "into any prompt. 'dicts' means that the "
            "return is a structured dictionary, containing "
            "more information such as full article content, "
            "and additional metadata (like a classic news api). "
            "Can be 'string' or 'dicts', or 'both'."
        ] = "dicts",
        historical: Annotated[
            bool,
            "Search on archive of historical news. "
            "Defaults to False, meaning that the search "
            "will only look through the most recent "
            "news (48 hours)"
        ] = False,
        method: Annotated[
            Literal["nl", "kw"],
            "Method to use for searching. 'nl' means Natural "
            "Language, which is a string that can be any "
            "phrase, keyword, question, or paragraph that will "
            "be used for semantic search on the news. "
            "'kw' means Keyword, which can also be any keyword(s),"
            " phrase, or paragraph, however the search is a "
            "direct keyword search on the database."
        ] = "nl",
        similarity_score_threshold: Annotated[
            float,
            "Similarity score threshold"
        ] = 0.5,
        offset: Annotated[
            int,
            "Offset for pagination. The n_articles is your page size, "
            "while your offset is the number of articles to skip to get"
            " to your page of interest. For example, if you want to get page 3 "
            "for n_article page size of 10, you would set offset to 20."
        ] = 0,
        categories: Annotated[
            list[
                Literal[
                    "All",
                    "Business",
                    "Crime",
                    "Politics",
                    "Science",
                    "Sports",
                    "Technology",
                    "Military",
                    "Health",
                    "Entertainment"
                ]
            ], "Categories of news to filter on"
        ] = ["All"],
        doc_start_delimiter: Annotated[str, "Document start delimiter"] = "<doc>",
        doc_end_delimiter: Annotated[str, "Document end delimiter"] = "</doc>",
    ) -> SearchResponse:
        """
        Search for news articles given a query.

        https://api.asknews.app/docs#/news/operation/search_news
        """
        response = await self.client.get(
            endpoint="/v1/news/search",
            query={
                "query": query,
                "n_articles": n_articles,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "return_type": return_type,
                "method": method,
                "historical": historical,
                "offset": offset,
                "categories": categories,
                "similarity_score_threshold": similarity_score_threshold,
                "doc_start_delimiter": doc_start_delimiter,
                "doc_end_delimiter": doc_end_delimiter,
            },
            accept=[(SearchResponse.__content_type__, 1.0)]
        )
        return SearchResponse.model_validate(response.content)
