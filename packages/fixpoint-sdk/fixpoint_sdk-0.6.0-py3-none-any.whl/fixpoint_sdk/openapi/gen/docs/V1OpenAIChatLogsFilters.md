# V1OpenAIChatLogsFilters


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**relative_datetime_filters** | [**V1RelativeDateTimeFilters**](V1RelativeDateTimeFilters.md) |  | [optional] 
**userfeedback_filter** | [**V1LikeFilter**](V1LikeFilter.md) |  | [optional] 
**attribute_filters** | [**V1AttributeFilters**](V1AttributeFilters.md) |  | [optional] 
**dataset_filters** | [**V1DatasetFilters**](V1DatasetFilters.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_open_ai_chat_logs_filters import V1OpenAIChatLogsFilters

# TODO update the JSON string below
json = "{}"
# create an instance of V1OpenAIChatLogsFilters from a JSON string
v1_open_ai_chat_logs_filters_instance = V1OpenAIChatLogsFilters.from_json(json)
# print the JSON string representation of the object
print(V1OpenAIChatLogsFilters.to_json())

# convert the object into a dict
v1_open_ai_chat_logs_filters_dict = v1_open_ai_chat_logs_filters_instance.to_dict()
# create an instance of V1OpenAIChatLogsFilters from a dict
v1_open_ai_chat_logs_filters_form_dict = v1_open_ai_chat_logs_filters.from_dict(v1_open_ai_chat_logs_filters_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


