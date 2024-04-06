# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring

import typing
import pytest

from openai.types.chat import ChatCompletionChunk

from fixpoint_sdk.completions import combine_chunks, FinishReason
from .mock_completions import new_chunks, new_chat_completion


def test_combine_chunks() -> None:
    chunks = new_chunks()
    completion = new_chat_completion()
    combined = combine_chunks(chunks)
    assert combined.id == completion.id
    assert combined.created == completion.created
    assert combined.model == completion.model
    assert combined.choices[0].finish_reason == completion.choices[0].finish_reason
    assert combined.choices[0].message.role == completion.choices[0].message.role
    assert combined.choices[0].message.content == completion.choices[0].message.content


def test_combine_multichoice_chunks() -> None:
    chunks = zip_choices(
        new_chunks(), new_chunks(), append_text="!", finish_reason="tool_calls"
    )
    completion = new_chat_completion()
    combined = combine_chunks(chunks)
    assert combined.id == completion.id
    assert combined.created == completion.created
    assert combined.model == completion.model
    assert combined.choices[0].finish_reason == completion.choices[0].finish_reason
    assert combined.choices[0].message.role == completion.choices[0].message.role
    assert combined.choices[0].message.content == completion.choices[0].message.content

    assert combined.choices[1].finish_reason == "tool_calls"
    # all output roles are the same: "assistant"
    assert (
        combined.choices[1].message.content
        == "!No!,! I! am! not! sentient!.! I! am! a! computer! program! designed! to! assist! with! tasks! and! provide! information!.!"  # pylint: disable=line-too-long
    )


def test_invalid_choices() -> None:
    chunks = zip_choices(new_chunks(), new_chunks(), drop_indexes={2})
    with pytest.raises(ValueError):
        combine_chunks(chunks)


def zip_choices(
    chunks1: typing.List[ChatCompletionChunk],
    chunks2: typing.List[ChatCompletionChunk],
    append_text: typing.Optional[str] = None,
    drop_indexes: typing.Optional[typing.Set[int]] = None,
    finish_reason: FinishReason = "stop",
) -> typing.List[ChatCompletionChunk]:
    """Zips chunks2 into chunks1, overwriting the choices in chunks1."""
    if not drop_indexes:
        drop_indexes = set()
    if len(chunks1) != len(chunks2):
        raise ValueError("Chunks must have the same length")
    if len(chunks1) == 0:
        return []

    for i, chunk in enumerate(chunks1):
        if i in drop_indexes:
            continue
        mixin_choice = chunks2[i].choices[0]
        mixin_choice.index = len(chunk.choices)
        if append_text and mixin_choice.delta.content is not None:
            mixin_choice.delta.content += append_text
        chunk.choices.append(mixin_choice)

    chunks1[-1].choices[1].finish_reason = finish_reason

    return chunks1
