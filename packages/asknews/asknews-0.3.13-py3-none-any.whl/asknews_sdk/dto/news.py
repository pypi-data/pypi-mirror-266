from __future__ import annotations

from typing import Annotated
from pydantic import Field

from asknews_sdk.dto.base import BaseSchema, Article


class SearchResponseDictItem(Article):
    as_string_key: Annotated[str, Field(title='As String Key')]


class SearchResponse(BaseSchema):
    as_dicts: Annotated[
        list[SearchResponseDictItem] | None, Field(title='As Dicts')
    ] = None
    as_string: Annotated[str | None, Field(title='As String')] = None
    offset: Annotated[int | None, Field(title='Offset Point')] = None
