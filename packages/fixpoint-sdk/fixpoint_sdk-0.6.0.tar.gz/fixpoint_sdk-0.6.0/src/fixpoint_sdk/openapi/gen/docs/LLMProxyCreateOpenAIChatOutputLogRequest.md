# LLMProxyCreateOpenAIChatOutputLogRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**input_name** | **str** |  | [optional] 
**openai_id** | **str** |  | [optional] 
**session_name** | **str** |  | [optional] 
**choices** | [**List[OpenAIChatOutputLogChoice]**](OpenAIChatOutputLogChoice.md) |  | [optional] 
**usage** | [**OpenAIChatOutputLogUsage**](OpenAIChatOutputLogUsage.md) |  | [optional] 
**trace_id** | **str** |  | [optional] 
**mode** | [**V1Mode**](V1Mode.md) |  | [optional] 

## Example

```python
from openapi_client.models.llm_proxy_create_open_ai_chat_output_log_request import LLMProxyCreateOpenAIChatOutputLogRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMProxyCreateOpenAIChatOutputLogRequest from a JSON string
llm_proxy_create_open_ai_chat_output_log_request_instance = LLMProxyCreateOpenAIChatOutputLogRequest.from_json(json)
# print the JSON string representation of the object
print(LLMProxyCreateOpenAIChatOutputLogRequest.to_json())

# convert the object into a dict
llm_proxy_create_open_ai_chat_output_log_request_dict = llm_proxy_create_open_ai_chat_output_log_request_instance.to_dict()
# create an instance of LLMProxyCreateOpenAIChatOutputLogRequest from a dict
llm_proxy_create_open_ai_chat_output_log_request_form_dict = llm_proxy_create_open_ai_chat_output_log_request.from_dict(llm_proxy_create_open_ai_chat_output_log_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


