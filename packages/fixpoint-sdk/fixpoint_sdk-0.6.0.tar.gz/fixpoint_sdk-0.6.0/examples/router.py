# pylint: disable=unused-variable

"""Examples using the inference router.

The inference router can send LLM inference requests to different models based
on configurable rules.
"""

import os

from fixpoint_sdk import openapi_client, ChatRouterClient
from fixpoint_sdk.openapi.exceptions import ApiException


def main(skip_creating_config: bool) -> None:
    """Example using inference router."""
    client = ChatRouterClient()
    if not skip_creating_config:
        # use this config to cap spend on all models
        # create_routing_config_all_capped(client)

        # Use this config to let the last model run forever after previous model
        # caps were reached.
        create_routing_config_last_uncapped(client)
    try:
        completion = client.chat.completions.create(
            mode="test",
            user="some-user-id",
            trace_id="some-trace-id",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What are you?"},
            ],
        )
    except ApiException as e:
        print(f"Exception when calling ChatCompletionsApi->create: {e}\n")

    print("Received chat completion inference response.")
    print(completion.completion)


def create_routing_config_all_capped(client: ChatRouterClient) -> None:
    """Create a routing config where all models are capped.

    Define routing configuration This example:

    1. Tries to use gpt-3.5-turbo-0125 until it has spent $0.0001.
    2. After that, it will try to use gpt-3.5-turbo-0301, until spending $0.0001.
    3. After that, it rejects requests.
    """
    routing_config_req = openapi_client.V1CreateRoutingConfigRequest(
        fallback_strategy=openapi_client.V1FallbackStrategy.FALLBACK_STRATEGY_NEXT,
        terminal_state=openapi_client.V1TerminalState.TERMINAL_STATE_ERROR,
        models=[
            openapi_client.V1Model(
                provider="openai",
                name="gpt-3.5-turbo-0125",
                spend_cap=openapi_client.V1SpendCap(
                    amount="0.0001",
                    currency="USD",
                    reset_interval=openapi_client.V1ResetInterval.RESET_INTERVAL_MONTHLY,
                ),
            ),
            openapi_client.V1Model(
                provider="openai",
                name="gpt-3.5-turbo-0301",
                spend_cap=openapi_client.V1SpendCap(
                    amount="0.0001",
                    currency="USD",
                    reset_interval=openapi_client.V1ResetInterval.RESET_INTERVAL_MONTHLY,
                ),
            ),
        ],
        description="This is a test routing config.",
    )

    try:
        routing_config = client.fixpoint.proxy_client.llm_proxy_create_routing_config(
            routing_config_req
        )
    except ApiException as e:
        print(
            f"Exception when calling LLMProxyApi->llm_proxy_create_routing_config: {e}\n"
        )
        raise
    print(f"Routing config created. ID = {routing_config.id}")


def create_routing_config_last_uncapped(client: ChatRouterClient) -> None:
    """Create a routing config where the last model is uncapped.

    Define routing configuration This example:

    1. Tries to use gpt-3.5-turbo-0125 until it has spent $0.0001.
    2. After that, it will use gpt-3.5-turbo-0301, without a spending cap.
    """
    routing_config_req = openapi_client.V1CreateRoutingConfigRequest(
        fallback_strategy=openapi_client.V1FallbackStrategy.FALLBACK_STRATEGY_NEXT,
        terminal_state=openapi_client.V1TerminalState.TERMINAL_STATE_IGNORE_CAP,
        models=[
            openapi_client.V1Model(
                provider="openai",
                name="gpt-3.5-turbo-0125",
                spend_cap=openapi_client.V1SpendCap(
                    amount="0.0001",
                    currency="USD",
                    reset_interval=openapi_client.V1ResetInterval.RESET_INTERVAL_MONTHLY,
                ),
            ),
            openapi_client.V1Model(
                provider="openai",
                name="gpt-3.5-turbo-0301",
            ),
        ],
        description="This is a test routing config.",
    )

    try:
        routing_config = client.fixpoint.proxy_client.llm_proxy_create_routing_config(
            routing_config_req
        )
        print(f"Routing config created. ID = {routing_config.id}")
    except ApiException as e:
        print(
            f"Exception when calling LLMProxyApi->llm_proxy_create_routing_config: {e}\n"
        )


if __name__ == "__main__":
    main(os.environ.get("SKIP_CREATING_CONFIG", "false").lower() == "true")
