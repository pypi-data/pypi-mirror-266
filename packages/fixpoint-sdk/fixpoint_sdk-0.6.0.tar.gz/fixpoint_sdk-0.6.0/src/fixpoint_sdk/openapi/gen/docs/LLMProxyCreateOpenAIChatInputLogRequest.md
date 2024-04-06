# LLMProxyCreateOpenAIChatInputLogRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_name** | **str** |  | [optional] 
**messages** | [**List[V1Message]**](V1Message.md) |  | [optional] 
**temperature** | **float** |  | [optional] 
**trace_id** | **str** |  | [optional] 
**user_id** | **str** |  | [optional] 
**mode** | [**V1Mode**](V1Mode.md) |  | [optional] 

## Example

```python
from openapi_client.models.llm_proxy_create_open_ai_chat_input_log_request import LLMProxyCreateOpenAIChatInputLogRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMProxyCreateOpenAIChatInputLogRequest from a JSON string
llm_proxy_create_open_ai_chat_input_log_request_instance = LLMProxyCreateOpenAIChatInputLogRequest.from_json(json)
# print the JSON string representation of the object
print(LLMProxyCreateOpenAIChatInputLogRequest.to_json())

# convert the object into a dict
llm_proxy_create_open_ai_chat_input_log_request_dict = llm_proxy_create_open_ai_chat_input_log_request_instance.to_dict()
# create an instance of LLMProxyCreateOpenAIChatInputLogRequest from a dict
llm_proxy_create_open_ai_chat_input_log_request_form_dict = llm_proxy_create_open_ai_chat_input_log_request.from_dict(llm_proxy_create_open_ai_chat_input_log_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


