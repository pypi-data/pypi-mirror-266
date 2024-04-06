from __future__ import annotations

from typing import Annotated, Any
from pydantic import BaseModel, Field, ConfigDict

from asknews_sdk.dto.base import BaseSchema


class CreateChatCompletionRequestMessage(BaseModel):
    role: Annotated[str, Field(title='Role')]
    content: Annotated[str, Field(title='Content')]
    name: Annotated[str | None, Field(None, title='Name')]
    function_call: Annotated[dict[str, Any] | None, Field(None, title='Function Call')]


class CreateChatCompletionResponseChoice(BaseModel):
    index: Annotated[int, Field(title='Index')]
    message: CreateChatCompletionRequestMessage
    finish_reason: Annotated[str | None, Field(None, title='Finish Reason')]


class CreateChatCompletionResponseStreamChoice(BaseModel):
    index: Annotated[int, Field(title='Index')]
    delta: CreateChatCompletionRequestMessage
    finish_reason: Annotated[str | None, Field(None, title='Finish Reason')]


class CreateChatCompletionResponseUsage(BaseModel):
    prompt_tokens: Annotated[int, Field(title='Prompt Tokens')]
    completion_tokens: Annotated[int, Field(title='Completion Tokens')]
    total_tokens: Annotated[int, Field(title='Total Tokens')]


class CreateChatCompletionRequest(BaseSchema):
    model_config = ConfigDict(
        extra='allow',
    )
    model: Annotated[str | None, Field('gpt-3.5-turbo-16k', title='Model')]
    messages: Annotated[
        list[CreateChatCompletionRequestMessage], Field(title='Messages')
    ]
    temperature: Annotated[float | None, Field(0.9, title='Temperature')]
    top_p: Annotated[float | None, Field(1.0, title='Top P')]
    n: Annotated[int | None, Field(1, title='N')]
    stream: Annotated[bool | None, Field(False, title='Stream')]
    stop: Annotated[str | list[str] | None, Field(None, title='Stop')]
    max_tokens: Annotated[int | None, Field(9999, title='Max Tokens')]
    presence_penalty: Annotated[int | None, Field(0, title='Presence Penalty')]
    frequency_penalty: Annotated[int | None, Field(0, title='Frequency Penalty')]
    user: Annotated[str | None, Field(None, title='User')]


class CreateChatCompletionResponse(BaseSchema):
    id: Annotated[str, Field(title='Id')]
    created: Annotated[int, Field(title='Created')]
    object: Annotated[str | None, Field('chat.completion', title='Object')]
    model: Annotated[str | None, Field('gpt-3.5-turbo-16k', title='Model')]
    usage: CreateChatCompletionResponseUsage
    choices: Annotated[list[CreateChatCompletionResponseChoice], Field(title='Choices')]


class CreateChatCompletionResponseStream(BaseSchema):
    __content_type__ = "text/event-stream"

    id: Annotated[str, Field(title='Id')]
    created: Annotated[int, Field(title='Created')]
    object: Annotated[str | None, Field('chat.completion.chunk', title='Object')]
    model: Annotated[str | None, Field('gpt-3.5-turbo-16k', title='Model')]
    usage: CreateChatCompletionResponseUsage
    choices: Annotated[
        list[CreateChatCompletionResponseStreamChoice], Field(title='Choices')
    ]
