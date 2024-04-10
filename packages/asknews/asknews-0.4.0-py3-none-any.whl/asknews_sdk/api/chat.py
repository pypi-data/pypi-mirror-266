from typing import AsyncIterator, Iterator, Literal

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.chat import (
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStream,
    ListModelResponse,
)

class ChatAPI(BaseAPI):
    """
    Chat API

    https://add-docs.review.docs.asknews.app/en/reference#tag--chat
    """
    def get_chat_completions(
        self,
        messages: list[dict[str, str]],
        model: Literal[
            "gpt-3.5-turbo-16k",
            "gpt-4-1106-preview",
            "mistral-small",
            "mixtral-8x7b-32768"
        ] = "gpt-3.5-turbo-16k",
        stream: bool = False,
    ) -> CreateChatCompletionResponse | Iterator[CreateChatCompletionResponseStream]:
        """
        Get chat completions for a given user message.

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/completions

        :param messages: List of messages in the conversation.
        :type messages: list[dict[str, str]]
        :param model: Model to use for chat completion, defaults to "gpt-3.5-turbo-16k"
        :type model: Literal[
            "gpt-3.5-turbo-16k", "gpt-4-1106-preview", "mistral-small", "mixtral-8x7b-32768"
        ]
        :param stream: Whether to stream the response, defaults to False
        :type stream: bool
        :return: Chat completions
        :rtype: CreateChatCompletionResponse | Iterator[CreateChatCompletionResponseStream]
        """
        response = self.client.request(
            method="POST",
            endpoint="/v1/openai/chat/completions",
            body=CreateChatCompletionRequest(
                messages=messages,
                model=model,
                stream=stream,
            ).model_dump(mode="json"),
            headers={
                "Content-Type": CreateChatCompletionRequest.__content_type__,
            },
            accept=[
                (CreateChatCompletionResponse.__content_type__, 1.0),
                (CreateChatCompletionResponseStream.__content_type__, 1.0),
            ],
            stream=stream,
            stream_type="lines"  # type: ignore
        )

        if stream:
            def _stream():
                for chunk in response.content:
                    if chunk.strip() == "data: [DONE]":
                        break

                    if chunk.startswith("data:"):
                        json_data = chunk.replace("data: ", "").strip()
                        yield CreateChatCompletionResponseStream.model_validate_json(json_data)

            return _stream()
        else:
            return CreateChatCompletionResponse.model_validate(response.content)

    def list_chat_models(self) -> ListModelResponse:
        """
        List available chat models.

        https://docs.asknews.app/en/reference#get-/v1/openai/models

        :return: List of available chat models
        :rtype: ListModelResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/openai/chat/models",
            accept=[(ListModelResponse.__content_type__, 1.0)]
        )
        return ListModelResponse.model_validate(response.content)

    def get_headline_questions(self, queries: list[str] | None = None) -> dict[str, list[str]]:
        """
        Get headline questions for a given query.

        https://docs.asknews.app/en/reference#get-/v1/chat/questions

        :param queries: List of queries to get headline questions for
        :type queries: list[str] | None
        :return: Headline questions
        :rtype: dict[str, list[str]]
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/chat/questions",
            query={"queries": queries}
        )
        return response.content


class AsyncChatAPI(BaseAPI):
    """
    Chat API

    https://api.asknews.app/docs#tag/chat
    """
    async def get_chat_completions(
        self,
        messages: list[dict[str, str]],
        model: Literal[
            "gpt-3.5-turbo-16k",
            "gpt-4-1106-preview",
            "mistral-small",
            "mixtral-8x7b-32768"
        ] = "gpt-3.5-turbo-16k",
        stream: bool = False,
    ) -> CreateChatCompletionResponse | AsyncIterator[CreateChatCompletionResponseStream]:
        """
        Get chat completions for a given user message.

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/completions

        :param messages: List of messages in the conversation.
        :type messages: list[dict[str, str]]
        :param model: Model to use for chat completion, defaults to "gpt-3.5-turbo-16k"
        :type model: Literal[
            "gpt-3.5-turbo-16k", "gpt-4-1106-preview", "mistral-small", "mixtral-8x7b-32768"
        ]
        :param stream: Whether to stream the response, defaults to False
        :type stream: bool
        :return: Chat completions
        :rtype: CreateChatCompletionResponse | AsyncIterator[CreateChatCompletionResponseStream]
        """
        response = await self.client.request(
            method="POST",
            endpoint="/v1/openai/chat/completions",
            body=CreateChatCompletionRequest(
                messages=messages,
                model=model,
                stream=stream,
            ).model_dump(mode="json"),
            headers={
                "Content-Type": CreateChatCompletionRequest.__content_type__,
            },
            accept=[
                (CreateChatCompletionResponse.__content_type__, 1.0),
                (CreateChatCompletionResponseStream.__content_type__, 1.0),
            ],
            stream=stream,
            stream_type="lines"  # type: ignore
        )

        if stream:
            async def _stream():
                async for chunk in response.content:
                    if chunk.strip() == "data: [DONE]":
                        break

                    if chunk.startswith("data:"):
                        json_data = chunk.replace("data: ", "").strip()
                        yield CreateChatCompletionResponseStream.model_validate_json(json_data)

            return _stream()
        else:
            return CreateChatCompletionResponse.model_validate(response.content)

    async def list_chat_models(self) -> ListModelResponse:
        """
        List available chat models.

        https://docs.asknews.app/en/reference#get-/v1/openai/models

        :return: List of available chat models
        :rtype: ListModelResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/openai/chat/models",
            accept=[(ListModelResponse.__content_type__, 1.0)]
        )
        return ListModelResponse.model_validate(response.content)

    async def get_headline_questions(
        self,
        queries: list[str] | None = None
    ) -> dict[str, list[str]]:
        """
        Get headline questions for a given query.

        https://docs.asknews.app/en/reference#get-/v1/chat/questions

        :param queries: List of queries to get headline questions for
        :type queries: list[str] | None
        :return: Headline questions
        :rtype: dict[str, list[str]]
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/chat/questions",
            query={"queries": queries}
        )
        return response.content
