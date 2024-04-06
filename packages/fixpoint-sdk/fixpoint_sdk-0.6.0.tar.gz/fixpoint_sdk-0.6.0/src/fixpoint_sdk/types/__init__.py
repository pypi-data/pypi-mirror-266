"""Type definitions for the Fixpoint SDK."""

from dataclasses import dataclass, asdict
import enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from openai.types.chat import ChatCompletionMessageParam


class ThumbsReaction(enum.Enum):
    """The specific user feedback reaction."""

    THUMBS_UNSPECIFIED = 0
    THUMBS_UP = 1
    THUMBS_DOWN = 2


class OriginType(enum.Enum):
    """The origin of a user feedback.

    User feedback can come from end-users, or it can come from the developers of
    the LLM deployment being monitored.
    """

    ORIGIN_UNSPECIFIED = 0
    ORIGIN_USER_FEEDBACK = 1
    ORIGIN_ADMIN = 2


class ModeType(enum.Enum):
    """The mode in which an entity is stored.

    There are three possible modes: test, staging, and prod. Any entity such as an LLM log or
    a dataset registered under a specific mode will only be accessible in that mode.
    If unspecified in the request, any entity will be stored in the prod mode by default.
    """

    MODE_UNSPECIFIED = 0
    MODE_TEST = 1
    MODE_STAGING = 2
    MODE_PROD = 3


ModeArg = Union[
    Literal["unspecified"],
    Literal["test"],
    Literal["staging"],
    Literal["prod"],
    Literal[0],
    Literal[1],
    Literal[2],
    Literal[3],
]


def parse_mode_type(mode: Optional[Union[str, int, object]] = None) -> ModeType:
    """Parse a mode type from a string."""
    if mode is None:
        return ModeType.MODE_UNSPECIFIED

    if isinstance(mode, int):
        return ModeType(mode)

    if isinstance(mode, str):
        if mode == "unspecified":
            return ModeType.MODE_UNSPECIFIED
        if mode == "test":
            return ModeType.MODE_TEST
        if mode == "staging":
            return ModeType.MODE_STAGING
        if mode == "prod":
            return ModeType.MODE_PROD
    raise ValueError(f"Unknown mode: {mode}")


@dataclass
class CreateLLMRoutingRequest:
    """Request to create a routing for an LLM."""

    messages: List[ChatCompletionMessageParam]
    temperature: Optional[float] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    mode: Optional[ModeType] = ModeType.MODE_UNSPECIFIED

    def to_dict(self) -> Dict[str, Any]:
        """Convert this request to a dictionary."""
        d = asdict(self)
        if self.mode is not None:
            d["mode"] = self.mode.value
        return d


@dataclass
class CreateLLMInputLogRequest:
    """Request to create a log of a chat completion input."""

    messages: List[ChatCompletionMessageParam]
    model_name: str
    user_id: Optional[str] = None
    temperature: Optional[float] = None
    trace_id: Optional[str] = None
    mode: Optional[ModeType] = ModeType.MODE_UNSPECIFIED

    def to_dict(self) -> Dict[str, Any]:
        """Convert this request to a dictionary."""
        d = asdict(self)
        # convert this to a JSON-serializable type
        if self.mode is not None:
            d["mode"] = self.mode.value
        return d


class OpenAILLMInputLog(TypedDict, total=False):
    """An input log with attributes from OpenAI response.

    This input log has some attributes that come directly from an OpenAI
    response. Some of the field names are slightly off from what our Fixpoint
    API expects, so we need to transform this to a `CreateLLMInputLogRequest`.
    """

    model: str
    messages: List[ChatCompletionMessageParam]
    user: Optional[str]
    temperature: Optional[float]
    trace_id: Optional[str]


# TODO(jakub) this is an incomplete definition.
class ChatCompletion(TypedDict):
    """A chat completion."""

    id: str
    choices: List[Any]
    created: int
    model: str
    object: Literal["chat.completion"]


# TODO(dbmikus) this is an incomplete definition.
class InputLog(TypedDict):
    """An LLM input log."""

    name: str
    modelName: Optional[str]
    sessionName: Optional[str]
    messages: List[Any]
    temperature: Optional[float]
    createdAt: Optional[Any]
    traceId: Optional[str]


# TODO(dbmikus) this is an incomplete definition.
class OutputLog(TypedDict):
    """An LLM output log."""

    name: str


class _UserFeedbackLike(TypedDict):
    log_name: str
    thumbs_reaction: ThumbsReaction
    user_id: str


class UserFeedbackLike(_UserFeedbackLike, total=False):
    """A user feedback like."""

    origin: Optional[OriginType]


class CreateUserFeedbackRequest(TypedDict):
    """Request to create a user feedback."""

    likes: List[UserFeedbackLike]


class CreateUserFeedbackResponse(TypedDict):
    """Response to a CreateUserFeedbackRequest."""

    success: bool


class LogAttributePartial(TypedDict):
    """A log attribute."""

    log_name: str
    key: str
    value: str


class CreateLogAttributeRequest(TypedDict):
    """Request to create a log attribute."""

    log_attribute: LogAttributePartial


class LogAttribute(TypedDict):
    """An attribute attached to an LLM log."""

    name: str
    logName: str
    key: str
    value: str
    orgId: str


class CreateLogLogAttributeResponse(TypedDict):
    """Response to a CreateLogAttributeRequest."""

    logAttribute: LogAttribute
