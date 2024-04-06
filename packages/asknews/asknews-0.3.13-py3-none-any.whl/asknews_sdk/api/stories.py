from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.stories import (
    StoriesResponse,
    StoryResponse,
    SourceReportResponse
)
from typing import Annotated, Literal
from uuid import UUID

class StoriesAPI(BaseAPI):
    """
    Stories API

    https://api.asknews.app/docs#/stories
    """
    async def search_stories(
        self,
        query: Annotated[
            str | None,
            "Query to be used for the search. If method='nl', then this will be"
            "used as a natural language query. If method='kw', then this will"
            "be used as a direct keyword query."
        ] = None,
        categories: Annotated[
            list[
                Literal[
                    "Politics",
                    "Economy",
                    "Finance",
                    "Science",
                    "Technology",
                    "Sports",
                    "Climate",
                    "Environment",
                    "Culture",
                    "Entertainment",
                    "Business",
                    "Health",
                    "International"
                ]
            ], "Categories to filter on."] = [],
        uuids: Annotated[list[UUID], "UUIDs to retrieve."] = [],
        start_timestamp: Annotated[
            int | None,
            "Start timestamp to filter results on."
        ] = None,
        end_timestamp: Annotated[int | None,
                                 "End timestamp to filter results on."
                                 ] = None,
        sort_by: Annotated[
            Literal["published", "coverage", "sentiment"] | None,
                "Whether to sort returned values by coverage, can be 'asc' or 'desc'"
        ] = None,
        sort_type: Annotated[
            Literal["asc", "desc"] | None,
            "Whether to sort by sentiment, can be 'asc' or 'desc'."
        ] = None,
        continent: Annotated[
            Literal[
                "Africa",
                "Asia",
                "Europe",
                "Middle East",
                "North America",
                "South America",
                "Oceania",
            ] | None,
            "Continent to filter by."
        ] = None,
        offset: Annotated[int | str | None, "Offset to use"] = None,
        limit: Annotated[int, "Limit to use"] = 50,
        expand_updates: Annotated[bool, "Whether to expand updates"] = False,
        max_updates: Annotated[int, "Max updates to use"] = 11,
        max_articles: Annotated[int, "Max articles to use per update"] = 5,
        reddit: Annotated[
            int,
            "Whether or not to include Reddit analysis"
            "where the integer indicates the number of threads"
            "to include in the response. 0 is default. Requires"
            "paid plan to access."

        ] = 0,
        method: Annotated[Literal["nl", "kw", "both"],
                          "Method to use for query, 'nl' means natural language, "
                          "and will run a semantic search on the stories database. "
                          "'kw' means keyword, and will search by keyword on the "
                          "stories database. 'both' means that "
                          "both methods will be used and results will be ranked "
                          "according to IRR."
                          ] = "kw",
        obj_type: Annotated[
            list[
                Literal["story", "story_update"]
            ],
                "Object type to filter by, can be a list with 'story' and/or 'story_update'"
        ] = ["story"]
    ) -> StoriesResponse:
        """
        Get the news stories.

        https://docs.asknews.app/#/stories/search_stories

        :param query: The query.
        :type query: str | None
        :param categories: The categories.
        :type categories: str | None
        :param start_timestamp: The start timestamp.
        :type start_timestamp: int | None
        :param end_timestamp: The end timestamp.
        :type end_timestamp: int | None
        :param sort_by_time: Whether to sort by time.
        :type sort_by_time: bool
        :param offset: The offset.
        :type offset: int
        :param reddit: include Reddit perspective in the response
        :type reddit: int
        :return: The stories response.
        :rtype: StoriesResponse
        """
        response = await self.client.get(
            endpoint="/v1/stories",
            query={
                "query": query,
                "categories": categories,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "offset": offset,
                "method": method,
                "sort_by": sort_by,
                "sort_type": sort_type,
                "obj_type": obj_type,
                "reddit": reddit,
                "limit": limit,
                "expand_updates": expand_updates,
                "max_updates": max_updates,
                "max_articles": max_articles,
                "uuids": uuids
            },
            # accept=[(StoriesResponse.__content_type__, 1.0)]
        )

        return StoriesResponse.model_validate(response.content)

    async def get_story(
        self,
        story_id: Annotated[UUID | str, "The story ID"],
        expand_updates: Annotated[bool, "Whether to expand updates"] = True,
        max_updates: Annotated[int, "Max updates to use"] = 11,
        max_articles: Annotated[int, "Max articles to use per update"] = 5,
        reddit: Annotated[int, "Whether or not to include Reddit analysis"] = 0,
    ) -> StoryResponse:
        """
        Get a single news story given the ID.

        https://docs.asknews.app/#/stories/get_story

        :param story_id: The story ID.
        :type story_id: str
        :return: The story response.
        :rtype: StoryResponse
        """
        response = await self.client.get(
            endpoint="/v1/stories/{story_id}",
            params={
                "expand_updates": expand_updates,
                "max_updates": max_updates,
                "max_articles": max_articles,
                "reddit": reddit
            },
            # accept=[(StoryResponse.__content_type__, 1.0)]
        )
        return StoryResponse.model_validate(response.content)

    async def get_sources_report(
        self,
        n_points: int = 100,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
        metric: str = "countries_diversity",
        sampling: str = "1h",
    ) -> SourceReportResponse:
        """
        Get the sources report.

        https://docs.asknews.app/#/stories/get_sources_report

        :param n_points: The number of points.
        :type n_points: int
        :param start_timestamp: The start timestamp.
        :type start_timestamp: int | None
        :param end_timestamp: The end timestamp.
        :type end_timestamp: int | None
        :param metric: The metric.
        :type metric: str
        :param sampling: The sampling.
        :type sampling: str
        :return: The source report response.
        :rtype: SourceReportResponse
        """
        response = await self.client.get(
            endpoint="/v1/stories/sources",
            query={
                "n_points": n_points,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "metric": metric,
                "sampling": sampling,
            },
            # accept=[(SourceReportResponse.__content_type__, 1.0)]
        )
        # return SourceReportResponse.model_validate(response.content)
        return response.content
