# V1OpenAIChatInputLog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**model_name** | **str** |  | [optional] 
**session_name** | **str** |  | [optional] 
**messages** | [**List[V1Message]**](V1Message.md) |  | [optional] 
**temperature** | **float** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**trace_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_open_ai_chat_input_log import V1OpenAIChatInputLog

# TODO update the JSON string below
json = "{}"
# create an instance of V1OpenAIChatInputLog from a JSON string
v1_open_ai_chat_input_log_instance = V1OpenAIChatInputLog.from_json(json)
# print the JSON string representation of the object
print(V1OpenAIChatInputLog.to_json())

# convert the object into a dict
v1_open_ai_chat_input_log_dict = v1_open_ai_chat_input_log_instance.to_dict()
# create an instance of V1OpenAIChatInputLog from a dict
v1_open_ai_chat_input_log_form_dict = v1_open_ai_chat_input_log.from_dict(v1_open_ai_chat_input_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


