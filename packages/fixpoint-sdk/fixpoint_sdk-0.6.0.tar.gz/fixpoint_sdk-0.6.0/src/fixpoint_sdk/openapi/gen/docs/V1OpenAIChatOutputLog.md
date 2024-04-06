# V1OpenAIChatOutputLog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**input_name** | **str** |  | [optional] 
**openai_id** | **str** |  | [optional] 
**model_name** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**choices** | [**List[OpenAIChatOutputLogChoice]**](OpenAIChatOutputLogChoice.md) |  | [optional] 
**usage** | [**OpenAIChatOutputLogUsage**](OpenAIChatOutputLogUsage.md) |  | [optional] 
**trace_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_open_ai_chat_output_log import V1OpenAIChatOutputLog

# TODO update the JSON string below
json = "{}"
# create an instance of V1OpenAIChatOutputLog from a JSON string
v1_open_ai_chat_output_log_instance = V1OpenAIChatOutputLog.from_json(json)
# print the JSON string representation of the object
print(V1OpenAIChatOutputLog.to_json())

# convert the object into a dict
v1_open_ai_chat_output_log_dict = v1_open_ai_chat_output_log_instance.to_dict()
# create an instance of V1OpenAIChatOutputLog from a dict
v1_open_ai_chat_output_log_form_dict = v1_open_ai_chat_output_log.from_dict(v1_open_ai_chat_output_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


