from __future__ import annotations

from typing import Annotated
from datetime import datetime
from uuid import UUID
from pydantic import AnyUrl, BaseModel, Field, RootModel

from asknews_sdk.dto.base import BaseSchema, Article, Entities


class RedditPerspective(BaseModel):
    sentiment: int
    relevant: bool
    summary: str


class RedditThread(BaseModel):
    author: str
    author_comment_karma: int
    author_link_karma: int
    body: str
    classification: list[str]
    comments: list[RedditComment]
    comments_count: int
    date: datetime
    entities: Entities
    id: UUID
    key_takeaways: list[str]
    keywords: list[str]
    sentiment: int
    subreddit_name: str
    subreddit_url: str
    summary: str
    title: str
    topic: str
    upvotes: int
    url: str


class RedditComment(BaseModel):
    author: str
    body: str
    date: datetime
    upvotes: int


class IntraClusterStatistics(BaseModel):
    cluster_articles_pct: float = {}
    cluster_countries_pct: float = {}
    cluster_domains_pct: float = {}
    cluster_languages_pct: float = {}
    cluster_probabilities: dict = {}


class StoryResponseUpdate(BaseModel):
    uuid: Annotated[UUID, Field(title='UUID of the story update')]
    cluster_articles: list[Article]
    prompt_articles: list[Article]
    n_articles: int
    entities: Entities
    headline: str
    story: str
    story_update_ts: int
    sources_urls: dict[str, int]
    languages_pct: dict[str, float]
    countries_pct: dict[str, float]
    key_takeaways: list[str]
    contradictions: list[str]
    continent: str
    people: list[str]
    locations: list[str]
    new_information: str
    image_url: AnyUrl
    url_safe_title: str
    story_uuid: UUID
    categories: list[str]
    image_prompt: str
    reddit_perspective: RedditPerspective
    reddit_threads: list[RedditThread]
    languages: dict[str, int]
    keywords: list[str]
    intra_cluster_statistics: IntraClusterStatistics
    silhouette_score: dict
    article_ids: list[UUID]
    countries: dict[str, int]
    markdown_citations: list[str]

class StoryResponse(BaseSchema):
    uuid: Annotated[UUID, Field(title='UUID')]
    categories: Annotated[list[str], Field(title='Categories')]
    countries: Annotated[dict[str, int], Field(title='Countries')]
    countries_pct: Annotated[dict[str, float], Field(title='Countries percentage')]
    current_update_uuid: Annotated[str, Field(title='Current update UUID')]
    requested_update_uuid: Annotated[str, Field(title='Requested update UUID')]
    generate_image: Annotated[bool, Field(title='Generate image flag')]
    keywords: Annotated[list[str], Field(title='Keywords')]
    languages: Annotated[dict[str, int], Field(title='Languages')]
    languages_pct: Annotated[dict[str, float], Field(title='Languages percentage')]
    locations: Annotated[list[str], Field(title='Locations mentioned')]
    meta_type: Annotated[str, Field(title='Meta type')]
    n_articles: Annotated[list[int], Field(title='Number of articles')]
    n_updates: Annotated[int, Field(title='Number of updates')]
    people: Annotated[list[str], Field(title='People mentioned')]
    reddit_sentiment: Annotated[list[int], Field(title='Reddit sentiment')]
    reddit_sentiment_timestamps: Annotated[list[int], Field(title='Reddit sentiment timestamps')]
    rolling_sentiment: Annotated[list[float], Field(title='Rolling sentiment')]
    sentiment: Annotated[list[int], Field(title='Sentiment')]
    sentiment_timestamps: Annotated[list[int], Field(title='Sentiment timestamps')]
    sources: Annotated[dict[str, int], Field(title='Sources')]
    sources_urls: Annotated[dict[str, int], Field(title='Sources URLs')]
    topic: Annotated[str, Field(title='Topic')]
    topics: Annotated[list[str], Field(title='Topics')]
    updates: Annotated[list[StoryResponseUpdate], Field(title='Updates')]
    updated_ts: Annotated[int, Field(title='Updated timestamp')]
    update_uuids: Annotated[list[str], Field(title='Update UUIDs')]


class StoriesResponse(BaseModel):
    stories: Annotated[list[StoryResponse], Field(title='Stories')]
    offset: Annotated[int | str | None, Field(title='Offset')]


class SourceReportItem(BaseModel):
    bson_date: Annotated[datetime, Field(title='Bson Date')]
    n_bucket: Annotated[int, Field(title='Number of Buckets')]
    n_selected: Annotated[int, Field(title='Number of Selected')]
    bucket_counts: Annotated[dict[str, int], Field(title='Bucket Counts')]
    selected_counts: Annotated[dict[str, int], Field(title='Selected Counts')]
    bucket_pct: Annotated[dict[str, float], Field(title='Bucket Percentage')]
    selected_pct: Annotated[dict[str, float], Field(title='Selected Percentage')]

class SourceReportResponse(BaseSchema, RootModel[list[SourceReportItem]]):
    root: Annotated[list[SourceReportItem], Field(title='SourceReportResponse')]
