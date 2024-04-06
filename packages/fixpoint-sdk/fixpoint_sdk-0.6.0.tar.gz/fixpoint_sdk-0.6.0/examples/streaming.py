"""An example streaming back the chat completion."""

from fixpoint_sdk import FixpointClient


def main() -> None:
    """An example of using FixpointClient to make LLM calls and record feedback."""

    # Make sure that the enviroment variables set:
    # - `FIXPOINT_API_KEY` is set to your Fixpoint API key
    # - `OPENAI_API_KEY` is set to your normal OpenAI API key
    # Create a FixpointClient instance (uses the FIXPOINT_API_KEY env var)
    client = FixpointClient()

    # Call create method on FixpointClient instance. You can specify a user to
    # associate with the request. The user will be automatically passed through
    # to OpenAI's API.
    resp = client.chat.completions.create(
        stream=True,
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are you?"},
        ],
        user="some-user-id",
    )
    print(f"Logged input with ID/name: {resp.input_log['name']}")
    # The output log is not available until we have streamed all outputs
    output_log = resp.output_log
    assert output_log is None
    text_contents = []

    # You can iterate via `resp.completions`, like below, or via `resp` directly like:
    #
    #     for chunk in resp:
    #         ...
    #
    # Pylint is getting this wrong
    # pylint: disable=not-an-iterable
    for chunk in resp.completion:
        content = chunk.choices[0].delta.content
        if content:
            text_contents.append(content)
    print(f"Output text: {''.join(text_contents)}")
    output_log = resp.output_log
    assert output_log is not None
    print(f"Logged output with ID/name: {output_log['name']}")


if __name__ == "__main__":
    main()
