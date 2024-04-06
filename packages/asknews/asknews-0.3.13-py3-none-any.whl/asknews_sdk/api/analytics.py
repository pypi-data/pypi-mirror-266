from datetime import datetime
from typing import Literal
from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.sentiment import FinanceResponse


class AnalyticsAPI(BaseAPI):
    """
    Sentiment API

    https://api.asknews.app/docs#/sentiment
    """
    async def get_asset_sentiment(
        self,
        asset: Literal[
            "bitcoin",
            "ethereum",
            "cardano",
            "uniswap",
            "ripple",
            "solana",
            "polkadot",
            "polygon",
            "chainlink",
            "tether",
            "dogecoin",
            "monero",
            "tron",
            "binance",
            "aave",
            "tesla",
            "microsoft",
            "amazon"
        ],
        metric: Literal[
            "news_positive",
            "news_negative",
            "news_total",
            "news_positive_weighted",
            "news_negative_weighted",
            "news_total_weighted",
        ] = "news_positive",
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> FinanceResponse:
        """
        Get the timeseries sentiment for an asset.

        https://docs.asknews.app/#/sentiment/get_asset_sentiment

        :param slug: The asset slug.
        :type slug: str
        :param metric: The sentiment metric.
        :type metric: str
        :param date_from: The start date in ISO format.
        :type date_from: str | datetime
        :param date_to: The end date in ISO format.
        :type date_to: str | datetime
        :return: The sentiment response.
        :rtype: FinanceResponse
        """
        response = await self.client.get(
            endpoint="/v1/analytics/finance/sentiment",
            query={
                "asset": asset,
                "metric": metric,
                "date_from": date_from,
                "date_to": date_to
            },
            accept=[(FinanceResponse.__content_type__, 1.0)]
        )
        return FinanceResponse.model_validate(response.content)
