from __future__ import annotations

from typing import Annotated
from pydantic import BaseModel, Field, RootModel
from datetime import datetime

from asknews_sdk.dto.base import BaseSchema, Article


class SearchResponseDictItem(Article):
    as_string_key: Annotated[str, Field(title='As String Key')]


class SearchResponse(BaseSchema):
    as_dicts: Annotated[
        list[SearchResponseDictItem] | None, Field(title='As Dicts')
    ] = None
    as_string: Annotated[str | None, Field(title='As String')] = None
    offset: Annotated[int | None, Field(title='Offset Point')] = None


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
