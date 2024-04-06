from typing import ClassVar
from pydantic import BaseModel
from datetime import datetime
from pydantic import AnyUrl
from typing import Annotated
from pydantic import Field
from uuid import UUID


class BaseSchema(BaseModel):
    __content_type__: ClassVar[str] = "application/json"


class Entities(BaseModel):
    DATE: list[str] = []
    EVENT: list[str] = []
    GPE: list[str] = []
    ORG: list[str] = []
    PERSON: list[str] = []
    NORP: list[str] = []
    CARDINAL: list[str] = []


class Article(BaseModel):
    article_id: Annotated[UUID, Field(title='Article Id')]
    article_url: Annotated[AnyUrl, Field(title='Article Url')]
    classification: Annotated[list[str], Field(title='Classification')]
    country: Annotated[str, Field(title='Country')]
    source_id: Annotated[str, Field(title='Source Id')]
    page_rank: Annotated[int, Field(title='Page Rank')]
    domain_url: Annotated[str, Field(title='Domain Url')]
    eng_title: Annotated[str, Field(title='English Title')]
    entities: Annotated[Entities, Field(title='Entities')]
    image_url: Annotated[str | None, Field(title='Image Url')] = None
    keywords: Annotated[list[str], Field(title='Keywords')]
    language: Annotated[str, Field(title='Language')]
    pub_date: Annotated[datetime, Field(title='Pubdate')]
    summary: Annotated[str, Field(title='Summary')]
    title: Annotated[str, Field(title='Title')]
    sentiment: Annotated[int, Field(title='Sentiment')]
    medoid_distance: Annotated[float | None, Field(title='Medoid Distance')] = None
    markdown_citation: Annotated[str, Field(title='Markdown Citation')] = ""
