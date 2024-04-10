from __future__ import annotations

from typing import Annotated
from pydantic import AwareDatetime, BaseModel, Field

from asknews_sdk.dto.base import BaseSchema


class FinanceResponseTimeSeriesData(BaseModel):
    datetime: Annotated[AwareDatetime, Field(title='Datetime')]
    value: Annotated[int, Field(title='Value')]


class FinanceResponseTimeSeries(BaseModel):
    timeseries: Annotated[
        list[FinanceResponseTimeSeriesData], Field(title='Timeseriesdata')
    ]


class FinanceResponse(BaseSchema):
    data: FinanceResponseTimeSeries
