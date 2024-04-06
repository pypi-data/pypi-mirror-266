# OpenAIChatOutputLogChoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **str** |  | [optional] 
**message** | [**V1Message**](V1Message.md) |  | [optional] 
**finish_reason** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.open_ai_chat_output_log_choice import OpenAIChatOutputLogChoice

# TODO update the JSON string below
json = "{}"
# create an instance of OpenAIChatOutputLogChoice from a JSON string
open_ai_chat_output_log_choice_instance = OpenAIChatOutputLogChoice.from_json(json)
# print the JSON string representation of the object
print(OpenAIChatOutputLogChoice.to_json())

# convert the object into a dict
open_ai_chat_output_log_choice_dict = open_ai_chat_output_log_choice_instance.to_dict()
# create an instance of OpenAIChatOutputLogChoice from a dict
open_ai_chat_output_log_choice_form_dict = open_ai_chat_output_log_choice.from_dict(open_ai_chat_output_log_choice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


