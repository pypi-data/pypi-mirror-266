"""Module for making requests to the Fixpoint API."""

import typing

import requests
from openai.types.chat import ChatCompletion

from .debugging import debug_log_function_io
from .. import types
from ..lib import exc

DEFAULT_TIMEOUT_S = 60

ApiCallback = typing.Callable[[str, typing.Any, typing.Any], None]


class Requester:
    """Makes requests to the Fixpoint API."""

    api_key: str
    base_url: str
    timeout_s: int
    _on_api_call: typing.Optional[ApiCallback]

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout_s: int = DEFAULT_TIMEOUT_S,
        _on_api_call: typing.Optional[ApiCallback] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_s = timeout_s

        if self.base_url[-1] == "/":
            self.base_url = self.base_url[:-1]

        self._on_api_call = _on_api_call

    @debug_log_function_io
    def create_openai_routed_log(
        self,
        request: types.OpenAILLMInputLog,
        trace_id: typing.Optional[str] = None,
        mode: types.ModeType = types.ModeType.MODE_UNSPECIFIED,
    ) -> types.ChatCompletion:
        """Create routed input log for an LLM inference request."""
        url = f"{self.base_url}/v1/router"
        input_log_req = types.CreateLLMRoutingRequest(
            messages=request["messages"],
            user_id=request.get("user", None),
            temperature=request.get("temperature", None),
            trace_id=trace_id,
            mode=mode,
        )

        return typing.cast(
            types.ChatCompletion,
            self._post_to_fixpoint(url, input_log_req.to_dict()).json(),
        )

    @debug_log_function_io
    def create_openai_input_log(
        self,
        model_name: str,
        request: types.OpenAILLMInputLog,
        trace_id: typing.Optional[str] = None,
        mode: types.ModeType = types.ModeType.MODE_UNSPECIFIED,
    ) -> types.InputLog:
        """Create an input log for an LLM inference request."""
        url = f"{self.base_url}/v1/openai_chats/{model_name}/input_logs"
        input_log_req = types.CreateLLMInputLogRequest(
            model_name=model_name,
            messages=request["messages"],
            user_id=request.get("user", None),
            temperature=request.get("temperature", None),
            trace_id=trace_id,
            mode=mode,
        )
        return typing.cast(
            types.InputLog, self._post_to_fixpoint(url, input_log_req.to_dict()).json()
        )

    @debug_log_function_io
    def create_openai_output_log(
        self,
        model_name: str,
        input_log_results: types.InputLog,
        open_ai_response: ChatCompletion,
        trace_id: typing.Optional[str] = None,
        mode: types.ModeType = types.ModeType.MODE_UNSPECIFIED,
    ) -> types.OutputLog:
        """Create an output log for an LLM inference response."""
        url = f"{self.base_url}/v1/openai_chats/{model_name}/output_logs"

        # If input_log_results doesn't have id then error
        if "name" not in input_log_results:
            raise ValueError("input_log_results must have a name")

        # If open_ai_response doesn't have id then error
        if not open_ai_response.id:
            raise ValueError("open_ai_response must have an id")

        choices = []
        for choice in open_ai_response.choices:
            choices.append(
                {
                    "index": str(choice.index),
                    "message": choice.message.model_dump(),
                    "finish_reason": choice.finish_reason,
                }
            )

        request_obj = {
            "input_name": input_log_results["name"],
            "openai_id": open_ai_response.id,
            "model_name": model_name,
            "choices": choices,
            "usage": (
                open_ai_response.usage.model_dump() if open_ai_response.usage else None
            ),
            "mode": mode.value,
        }

        # If trace_id exists, add it to the requestObj
        if trace_id:
            request_obj["trace_id"] = trace_id

        return typing.cast(
            types.OutputLog, self._post_to_fixpoint(url, request_obj).json()
        )

    @debug_log_function_io
    def create_user_feedback(
        self, request: types.CreateUserFeedbackRequest
    ) -> types.CreateUserFeedbackResponse:
        """Create user feedback on an LLM log."""
        url = f"{self.base_url}/v1/likes"

        if "likes" not in request:
            raise ValueError("request must have a likes")

        if not isinstance(request["likes"], list):
            raise ValueError("request.likes must be a list")

        fixed_req: typing.Dict[str, typing.Any] = typing.cast(
            typing.Dict[str, typing.Any], request.copy()
        )
        fixed_req["likes"] = []

        for like in request["likes"]:
            new_like: typing.Dict[str, typing.Any] = typing.cast(
                typing.Dict[str, typing.Any], like.copy()
            )
            if "log_name" not in like:
                raise ValueError("request must have a log_name")

            if "thumbs_reaction" not in like:
                raise ValueError("request must have a thumbs_reaction")
            new_like["thumbs_reaction"] = like["thumbs_reaction"].value

            if "user_id" not in like:
                raise ValueError("request must have a user_id")

            new_like["origin"] = types.OriginType.ORIGIN_USER_FEEDBACK.value
            fixed_req["likes"].append(new_like)

        resp = self._post_to_fixpoint(url, fixed_req)
        return typing.cast(types.CreateUserFeedbackResponse, resp.json())

    @debug_log_function_io
    def create_attribute(
        self, request: types.CreateLogAttributeRequest
    ) -> types.LogAttribute:
        """Create a LLM log attribute and attach it to that LLM log."""
        url = f"{self.base_url}/v1/attributes"

        if "log_attribute" not in request:
            raise ValueError("request must have a log_attribute")

        log_attribute = request["log_attribute"]

        if "key" not in log_attribute:
            raise ValueError("log_attribute must have a key")

        if "value" not in log_attribute:
            raise ValueError("log_attribute must have a value")

        if "log_name" not in log_attribute:
            raise ValueError("log_attribute must have a log_name")

        resp = self._post_to_fixpoint(
            url, typing.cast(typing.Dict[str, typing.Any], request)
        )
        log_attr_resp = typing.cast(types.CreateLogLogAttributeResponse, resp.json())
        return log_attr_resp["logAttribute"]

    @debug_log_function_io
    def _post_to_fixpoint(
        self, url: str, req_or_resp_obj: typing.Dict[str, typing.Any]
    ) -> requests.Response:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        resp = requests.post(
            url, headers=headers, json=req_or_resp_obj, timeout=self.timeout_s
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise exc.ApiException(e.response.status_code, e.response.text) from e
        if self._on_api_call:
            self._on_api_call(url, req_or_resp_obj, resp.json())
        return resp
