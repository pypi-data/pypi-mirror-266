# V1AppLog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**trace_id** | **str** |  | [optional] 
**level** | [**AppLogLevelType**](AppLogLevelType.md) |  | [optional] 
**message** | **str** |  | [optional] 
**additional_info** | **object** |  | [optional] 
**event_timestamp** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.v1_app_log import V1AppLog

# TODO update the JSON string below
json = "{}"
# create an instance of V1AppLog from a JSON string
v1_app_log_instance = V1AppLog.from_json(json)
# print the JSON string representation of the object
print(V1AppLog.to_json())

# convert the object into a dict
v1_app_log_dict = v1_app_log_instance.to_dict()
# create an instance of V1AppLog from a dict
v1_app_log_form_dict = v1_app_log.from_dict(v1_app_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


