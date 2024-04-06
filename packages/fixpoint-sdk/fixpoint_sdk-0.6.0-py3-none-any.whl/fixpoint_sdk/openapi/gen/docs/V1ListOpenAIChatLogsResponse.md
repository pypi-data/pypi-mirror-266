# V1ListOpenAIChatLogsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**logs** | [**List[V1OpenAIChatLog]**](V1OpenAIChatLog.md) |  | [optional] 
**next_page_token** | **str** |  | [optional] 
**total_entries** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_list_open_ai_chat_logs_response import V1ListOpenAIChatLogsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListOpenAIChatLogsResponse from a JSON string
v1_list_open_ai_chat_logs_response_instance = V1ListOpenAIChatLogsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListOpenAIChatLogsResponse.to_json())

# convert the object into a dict
v1_list_open_ai_chat_logs_response_dict = v1_list_open_ai_chat_logs_response_instance.to_dict()
# create an instance of V1ListOpenAIChatLogsResponse from a dict
v1_list_open_ai_chat_logs_response_form_dict = v1_list_open_ai_chat_logs_response.from_dict(v1_list_open_ai_chat_logs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


