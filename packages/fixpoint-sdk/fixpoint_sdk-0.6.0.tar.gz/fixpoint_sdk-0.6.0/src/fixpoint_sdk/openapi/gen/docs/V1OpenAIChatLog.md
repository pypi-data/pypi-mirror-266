# V1OpenAIChatLog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name identifer of the chat log. | [optional] 
**model_name** | **str** | The model name that produced the log. | [optional] 
**app_name** | **str** |  | [optional] 
**data_source_name** | **str** |  | [optional] 
**session_name** | **str** |  | [optional] 
**input_log** | [**V1OpenAIChatInputLog**](V1OpenAIChatInputLog.md) |  | [optional] 
**output_log** | [**V1OpenAIChatOutputLog**](V1OpenAIChatOutputLog.md) |  | [optional] 
**created_at** | **datetime** | The created_at timestamp is the same as the input_log.created_at timestamp. | [optional] 

## Example

```python
from openapi_client.models.v1_open_ai_chat_log import V1OpenAIChatLog

# TODO update the JSON string below
json = "{}"
# create an instance of V1OpenAIChatLog from a JSON string
v1_open_ai_chat_log_instance = V1OpenAIChatLog.from_json(json)
# print the JSON string representation of the object
print(V1OpenAIChatLog.to_json())

# convert the object into a dict
v1_open_ai_chat_log_dict = v1_open_ai_chat_log_instance.to_dict()
# create an instance of V1OpenAIChatLog from a dict
v1_open_ai_chat_log_form_dict = v1_open_ai_chat_log.from_dict(v1_open_ai_chat_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


