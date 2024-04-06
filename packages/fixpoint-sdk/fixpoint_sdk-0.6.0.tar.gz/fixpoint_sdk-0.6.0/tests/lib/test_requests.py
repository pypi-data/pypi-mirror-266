# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring
# pylint: disable=line-too-long

import dataclasses
import typing

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    chat_completion,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage
import requests_mock

from fixpoint_sdk import types as fixtypes
from fixpoint_sdk.lib import requests as fixrequests
from fixpoint_sdk import ThumbsReaction


@dataclasses.dataclass
class CallRecords:
    url: str
    request: typing.Any
    response: typing.Any


class CallbackRequester(fixrequests.Requester):
    calls: typing.List[CallRecords]

    def __init__(
        self,
        api_key: str,
        base_url: str,
    ):
        def callback(url: str, request: typing.Any, response: typing.Any) -> None:
            self.calls.append(CallRecords(url, request, response))

        super().__init__(api_key, base_url, _on_api_call=callback)
        self.calls = []


def new_requester() -> CallbackRequester:
    return CallbackRequester("api_key", "http://localhost:8081")


def test_create_openai_input_log() -> None:
    url, req = new_create_openai_input_log_post_request()
    out = new_create_openai_input_log_output()
    args = new_create_openai_input_log_args()
    requester = new_requester()

    with requests_mock.Mocker() as m:
        m.post(url, json=out)
        requester.create_openai_input_log(*args)

    assert requester.calls[0].url == url
    assert requester.calls[0].request == req
    assert requester.calls[0].response == out


def new_create_openai_input_log_args() -> (
    typing.Tuple[str, fixtypes.OpenAILLMInputLog, str, fixtypes.ModeType]
):
    model_name = "gpt-3.5-turbo-0125"
    messages: typing.List[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are you?"},
    ]
    trace_id = "trace-id-in"
    openai_req: fixtypes.OpenAILLMInputLog = {"messages": messages, "user": "dylan-uid"}
    mode = fixtypes.ModeType.MODE_TEST
    return model_name, openai_req, trace_id, mode


def new_create_openai_input_log_post_request() -> (
    typing.Tuple[str, typing.Dict[str, typing.Any]]
):
    request_url = "http://localhost:8081/v1/openai_chats/gpt-3.5-turbo-0125/input_logs"
    request_json = {
        "model_name": "gpt-3.5-turbo-0125",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are you?"},
        ],
        "user_id": "dylan-uid",
        "trace_id": "trace-id-in",
        "temperature": None,
        "mode": fixtypes.ModeType.MODE_TEST.value,
    }
    return request_url, request_json


def new_create_openai_input_log_output() -> typing.Dict[str, typing.Any]:
    return {
        "name": "5b7c03aa-929f-48cd-81d4-ac69feeb63a5",
        "modelName": "gpt-3.5-turbo-0125",
        "sessionName": "",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are you?"},
        ],
        "temperature": 0,
        "createdAt": None,
        "traceId": "trace-id-in",
        "mode": fixtypes.ModeType.MODE_TEST.value,
    }


def test_create_openai_output_log() -> None:
    url, req = new_create_openai_output_log_post_request()
    out = new_create_openai_output_log_output()
    args = new_create_openai_output_log_args()
    requester = new_requester()

    with requests_mock.Mocker() as m:
        m.post(url, json=out)
        requester.create_openai_output_log(*args)

    assert requester.calls[0].url == url
    assert requester.calls[0].request == req
    assert requester.calls[0].response == out


def new_create_openai_output_log_args() -> (
    typing.Tuple[str, fixtypes.InputLog, ChatCompletion, str, fixtypes.ModeType]
):
    model_name = "gpt-3.5-turbo-0125"
    input_log_results: fixtypes.InputLog = {
        "name": "462ab380-b51e-4b6c-bed4-efc48ff27ee6",
        "modelName": "gpt-3.5-turbo-0125",
        "sessionName": "",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are you?"},
        ],
        "temperature": 0,
        "createdAt": None,
        "traceId": "",
    }
    open_ai_response = ChatCompletion(
        id="chatcmpl-8y9PZoZGSd7SZDXRLqYCB0FbUD2R7",
        choices=[
            chat_completion.Choice(
                finish_reason="stop",
                index=0,
                logprobs=None,
                message=ChatCompletionMessage(
                    content="I am a computer program designed to assist and provide information to users like yourself. How can I help you today?",
                    role="assistant",
                    function_call=None,
                    tool_calls=None,
                ),
            )
        ],
        created=1709346549,
        model="gpt-3.5-turbo-0125",
        object="chat.completion",
        system_fingerprint="fp_2b778c6b35",
        usage=CompletionUsage(completion_tokens=23, prompt_tokens=21, total_tokens=44),
    )
    trace_id = "trace-id-out"
    mode = fixtypes.ModeType.MODE_TEST
    return model_name, input_log_results, open_ai_response, trace_id, mode


def new_create_openai_output_log_post_request() -> (
    typing.Tuple[str, typing.Dict[str, typing.Any]]
):
    request_url = "http://localhost:8081/v1/openai_chats/gpt-3.5-turbo-0125/output_logs"
    request_json = {
        "input_name": "462ab380-b51e-4b6c-bed4-efc48ff27ee6",
        "openai_id": "chatcmpl-8y9PZoZGSd7SZDXRLqYCB0FbUD2R7",
        "model_name": "gpt-3.5-turbo-0125",
        "choices": [
            {
                "index": "0",
                "message": {
                    "content": "I am a computer program designed to assist and provide information to users like yourself. How can I help you today?",
                    "role": "assistant",
                    "function_call": None,
                    "tool_calls": None,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"completion_tokens": 23, "prompt_tokens": 21, "total_tokens": 44},
        "trace_id": "trace-id-out",
        "mode": fixtypes.ModeType.MODE_TEST.value,
    }
    return request_url, request_json


def new_create_openai_output_log_output() -> typing.Dict[str, typing.Any]:
    return {
        "name": "c5d5b9e8-4925-48ca-a7b7-e2086b44a066",
        "inputName": "462ab380-b51e-4b6c-bed4-efc48ff27ee6",
        "openaiId": "chatcmpl-8y9PZoZGSd7SZDXRLqYCB0FbUD2R7",
        "modelName": "gpt-3.5-turbo-0125",
        "createdAt": None,
        "choices": [
            {
                "index": "0",
                "message": {
                    "role": "assistant",
                    "content": "I am a computer program designed to assist and provide information to users like yourself. How can I help you today?",
                },
                "finishReason": "stop",
            }
        ],
        "usage": None,
        "traceId": "trace-id-out",
        "mode": fixtypes.ModeType.MODE_TEST.value,
    }


def test_create_user_feedback() -> None:
    url, req = new_create_user_feedback_http_request()
    out = new_create_user_feedback_return()
    args = new_create_user_feedback_args()
    requester = new_requester()

    with requests_mock.Mocker() as m:
        m.post(url, json=out)
        requester.create_user_feedback(args)

    assert requester.calls[0].url == url
    assert requester.calls[0].request == req
    assert requester.calls[0].response == out


def new_create_user_feedback_args() -> fixtypes.CreateUserFeedbackRequest:
    return {
        "likes": [
            {
                "log_name": "e7aaa35f-c894-4da4-95bd-671df9b90a71",
                "thumbs_reaction": ThumbsReaction.THUMBS_UP,
                "user_id": "foobar",
                "origin": None,
            }
        ]
    }


def new_create_user_feedback_return() -> typing.Dict[str, typing.Any]:
    return {"success": True}


def new_create_user_feedback_http_request() -> (
    typing.Tuple[str, typing.Dict[str, typing.Any]]
):
    url = "http://localhost:8081/v1/likes"
    req = {
        "likes": [
            {
                "log_name": "e7aaa35f-c894-4da4-95bd-671df9b90a71",
                "thumbs_reaction": 1,
                "user_id": "foobar",
                "origin": 1,
            }
        ]
    }
    return url, req


def test_create_attribute() -> None:
    url, req = new_create_attributes_http_request()
    out = new_create_attribute_return()
    args = new_create_attribute_args()
    requester = new_requester()

    with requests_mock.Mocker() as m:
        m.post(url, json=out)
        requester.create_attribute(args)

    assert requester.calls[0].url == url
    assert requester.calls[0].request == req
    assert requester.calls[0].response == out


def new_create_attribute_args() -> fixtypes.CreateLogAttributeRequest:
    return {
        "log_attribute": {
            "log_name": "e7aaa35f-c894-4da4-95bd-671df9b90a71",
            "key": "conversion",
            "value": "true",
        }
    }


def new_create_attribute_return() -> typing.Dict[str, typing.Any]:
    return {
        "logAttribute": {
            "name": "d0b0e41c-6a1a-476d-85d7-eecc3e377026",
            "logName": "e7aaa35f-c894-4da4-95bd-671df9b90a71",
            "key": "conversion",
            "value": "true",
            "orgId": "",
        }
    }


def new_create_attributes_http_request() -> (
    typing.Tuple[str, typing.Dict[str, typing.Any]]
):
    url = "http://localhost:8081/v1/attributes"
    req = {
        "log_attribute": {
            "log_name": "e7aaa35f-c894-4da4-95bd-671df9b90a71",
            "key": "conversion",
            "value": "true",
        }
    }
    return url, req
