"""Code for chat completions."""

import typing
from typing import Optional, Literal, List, Generator
from dataclasses import dataclass

from openai import OpenAI
from openai._streaming import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from .lib.requests import Requester
from .lib.debugging import dprint
from .lib.iterwrapper import IterWrapper
from .lib.logging import logger
from . import types


Model = typing.Union[
    str,
    Literal[
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-16k-0613",
    ],
]


@dataclass
class FixpointChatRoutedCompletion:
    """Wraps the OpenAI chat completion with logging data."""

    completion: types.ChatCompletion


@dataclass
class FixpointChatCompletion:
    """Wraps the OpenAI chat completion with logging data."""

    completion: ChatCompletion
    input_log: types.InputLog
    output_log: types.OutputLog


class FixpointChatCompletionStream:
    """Wraps the OpenAI chat completion stream with logging data."""

    _stream: Stream[ChatCompletionChunk]
    input_log: types.InputLog
    _output_log: typing.Optional[types.OutputLog]
    _outputs: typing.List[ChatCompletionChunk]
    _mode_type: types.ModeType
    _requester: Requester
    _trace_id: typing.Optional[str]
    _model_name: str
    _all_streamed: bool = False

    def __init__(
        self,
        *,
        stream: Stream[ChatCompletionChunk],
        input_log: types.InputLog,
        mode_type: types.ModeType,
        requester: Requester,
        trace_id: typing.Optional[str] = None,
        model_name: str,
    ):
        self.input_log = input_log
        self._output_log = None
        self._mode_type = mode_type
        self._requester = requester
        self._trace_id = trace_id
        self._model_name = model_name

        self._stream = stream
        self._outputs = []
        self._all_streamed = False

        def on_finish() -> None:
            self._all_streamed = True
            # Send HTTP request after calling create
            try:
                output_resp = self._requester.create_openai_output_log(
                    self._model_name,
                    self.input_log,
                    combine_chunks(self._outputs),
                    trace_id=self._trace_id,
                    mode=self._mode_type,
                )
                dprint(f"Created an output log: {output_resp['name']}")
                self._output_log = output_resp
            # pylint: disable=broad-exception-caught
            except Exception:
                # TODO(dbmikus) log the error here, but don't pollute client logs
                pass

        def on_error(exc: Exception) -> None:
            raise exc

        self._iter_wrapper = IterWrapper(
            stream, on_iter=self._outputs.append, on_finish=on_finish, on_error=on_error
        )

    def __next__(self) -> ChatCompletionChunk:
        return self._iter_wrapper.__next__()

    # pylint: disable=use-yield-from
    def __iter__(self) -> typing.Iterator[ChatCompletionChunk]:
        """Yield the chat completion chunks."""
        return self

    @property
    def completion(self) -> Generator[ChatCompletionChunk, None, None]:
        """Yield the chat completion chunks."""
        for chunk in self:
            yield chunk

    # This function is deprecated, because `completion` exists on all inference
    # response types while `completions` only exists on streaming response.
    @property
    def completions(self) -> Generator[ChatCompletionChunk, None, None]:
        """Yield the chat completion chunks."""
        return self.completion

    @property
    def output_log(self) -> typing.Optional[types.OutputLog]:
        """Returns the output log if we have streamed all output chunks."""
        if not self._all_streamed:
            logger.warning(
                "\n".join(
                    [
                        "FixpointChatCompletionStream.output_log error: stream all output chunks before accessing output_log.",  # pylint: disable=line-too-long
                        "\tStream by either iterating over the FixpointChatCompletionStream object, or its FixpointChatCompletionStream.completions property.",  # pylint: disable=line-too-long
                    ]
                )
            )
        return self._output_log


FinishReason = typing.Literal[
    "stop", "length", "tool_calls", "content_filter", "function_call"
]


def combine_chunks(chunks: typing.List[ChatCompletionChunk]) -> ChatCompletion:
    """Combine chunks from a stream into one full completion object."""
    if len(chunks) == 0:
        raise ValueError("Must have at least one chunk")

    num_choices = 0
    for chunk in chunks:
        if num_choices == 0:
            num_choices = len(chunk.choices)
        elif num_choices != len(chunk.choices):
            raise ValueError("All chunks must have the same number of choices")

    chatid = ""
    created = 0
    model = ""
    choice_contents: typing.List[typing.List[str]] = [[] for _ in range(num_choices)]
    # default to "assistant" for typing reasons
    # default to "stop" for typing reasons
    finish_reasons: typing.List[FinishReason] = ["stop" for _ in range(num_choices)]
    for chunk in chunks:
        # all `id` and `created` values are the same.
        chatid = chunk.id
        created = chunk.created
        model = chunk.model
        for choice in chunk.choices:
            if choice.delta.content is not None:
                choice_contents[choice.index].append(choice.delta.content)
            # default to "stop" for typing reasons
            finish_reasons[choice.index] = choice.finish_reason or "stop"

    final_choices = []
    for i, choice_content in enumerate(choice_contents):
        final_choices.append(
            Choice(
                index=i,
                finish_reason=finish_reasons[i],
                logprobs=None,
                message=ChatCompletionMessage(
                    # all output roles are assistants
                    role="assistant",
                    content="".join(choice_content),
                ),
            )
        )

    return ChatCompletion(
        id=chatid,
        created=created,
        model=model,
        object="chat.completion",
        # The server will compute this when logging
        usage=None,
        choices=final_choices,
    )


class Completions:
    """Create chat completion inferences and log them."""

    def __init__(self, requester: Requester, client: OpenAI):
        self.client = client
        self._requester = requester

    @typing.overload
    def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Model,
        stream: Optional[Literal[False]],
        **kwargs: typing.Any,
    ) -> FixpointChatCompletion: ...

    @typing.overload
    def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Model,
        stream: Literal[True],
        **kwargs: typing.Any,
    ) -> FixpointChatCompletionStream: ...

    @typing.overload
    def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Model,
        stream: bool,
        **kwargs: typing.Any,
    ) -> typing.Union[FixpointChatCompletion, FixpointChatCompletionStream]: ...

    @typing.overload
    def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Model,
        stream: typing.Union[Optional[Literal[False]], Literal[True]] = None,
        **kwargs: typing.Any,
    ) -> typing.Union[FixpointChatCompletion, FixpointChatCompletionStream]: ...

    def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Model,
        stream: typing.Union[Optional[Literal[False]], Literal[True]] = None,
        mode: Optional[types.ModeArg] = "unspecified",
        **kwargs: typing.Any,
    ) -> typing.Union[FixpointChatCompletion, FixpointChatCompletionStream]:
        """Create an OpenAI completion and log the LLM input and output."""
        # Do not mutate the input kwargs. That is an unexpected behavior for
        # our caller.
        kwargs = kwargs.copy()
        # Extract trace_id from kwargs, if it exists, otherwise set it to None
        trace_id = kwargs.pop("trace_id", None)
        mode_type = types.parse_mode_type(mode)

        # Deep copy the kwargs to avoid modifying the original
        req_copy = kwargs.copy()
        req_copy["model_name"] = model
        req_copy["messages"] = messages

        # Send HTTP request before calling create
        input_resp = self._requester.create_openai_input_log(
            req_copy["model_name"],
            # TODO(dbmikus) fix sloppy typing
            typing.cast(types.OpenAILLMInputLog, req_copy),
            trace_id=trace_id,
            mode=mode_type,
        )
        dprint(f'Created an input log: {input_resp["name"]}')

        if stream:
            openai_response = self.client.chat.completions.create(
                messages=messages, model=model, stream=stream, **kwargs
            )
            dprint("Received an openai response stream")
            return FixpointChatCompletionStream(
                stream=openai_response,
                input_log=input_resp,
                mode_type=mode_type,
                requester=self._requester,
                trace_id=trace_id,
                model_name=req_copy["model_name"],
            )

        openai_response = self.client.chat.completions.create(
            messages=messages, model=model, stream=stream, **kwargs
        )
        dprint(f"Received an openai response: {openai_response.id}")
        # Send HTTP request after calling create
        output_resp = self._requester.create_openai_output_log(
            req_copy["model_name"],
            input_resp,
            openai_response,
            trace_id=trace_id,
            mode=mode_type,
        )
        dprint(f"Created an output log: {output_resp['name']}")
        return FixpointChatCompletion(
            completion=openai_response,
            input_log=input_resp,
            output_log=output_resp,
        )


class RoutedCompletions:
    """Create chat completion inferences and log them."""

    def __init__(self, requester: Requester, client: OpenAI):
        self._requester = requester
        self._client = client

    def create(
        self,
        mode: Optional[types.ModeArg] = "unspecified",
        **kwargs: typing.Any,
    ) -> FixpointChatRoutedCompletion:
        """Create an OpenAI completion and log the LLM input and output."""
        # Prepare the request
        req_copy = kwargs.copy()
        trace_id = kwargs.pop("trace_id", None)

        routed_log_resp = self._requester.create_openai_routed_log(
            typing.cast(types.OpenAILLMInputLog, req_copy),
            mode=types.parse_mode_type(mode),
            trace_id=trace_id,
        )
        dprint(f"Created a routed log: {routed_log_resp['id']}")

        return FixpointChatRoutedCompletion(
            completion=routed_log_resp,
        )


class ChatWithRouter:
    """The Chat class lets you interact with the underlying chat APIs."""

    def __init__(self, requester: Requester, client: OpenAI):
        self.completions = RoutedCompletions(requester, client)


class Chat:
    """The Chat class lets you interact with the underlying chat APIs."""

    def __init__(self, requester: Requester, client: OpenAI):
        self.completions = Completions(requester, client)
