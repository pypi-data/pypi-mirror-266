"""Compatibility layer to make API changes more backwards compatible

When we make breaking API changes, this compatibility layer helps make those
changes more backwards compatible and easier to upgrade to.
"""

from typing import Tuple

from openai.types.chat import ChatCompletion

from . import types
from .completions import FixpointChatCompletion


def unwrap_chat_completion(
    completion: FixpointChatCompletion,
) -> Tuple[ChatCompletion, types.InputLog, types.OutputLog]:
    """Unwrap FixpointChatCompletion object to old tuple return value"""
    return completion.completion, completion.input_log, completion.output_log
