# OpenAIChatOutputLogUsage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt_tokens** | **int** |  | [optional] 
**completion_tokens** | **int** |  | [optional] 
**total_tokens** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.open_ai_chat_output_log_usage import OpenAIChatOutputLogUsage

# TODO update the JSON string below
json = "{}"
# create an instance of OpenAIChatOutputLogUsage from a JSON string
open_ai_chat_output_log_usage_instance = OpenAIChatOutputLogUsage.from_json(json)
# print the JSON string representation of the object
print(OpenAIChatOutputLogUsage.to_json())

# convert the object into a dict
open_ai_chat_output_log_usage_dict = open_ai_chat_output_log_usage_instance.to_dict()
# create an instance of OpenAIChatOutputLogUsage from a dict
open_ai_chat_output_log_usage_form_dict = open_ai_chat_output_log_usage.from_dict(open_ai_chat_output_log_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


