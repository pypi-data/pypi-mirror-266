# V1ListAppLogsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_logs** | [**List[V1AppLog]**](V1AppLog.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_list_app_logs_response import V1ListAppLogsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListAppLogsResponse from a JSON string
v1_list_app_logs_response_instance = V1ListAppLogsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListAppLogsResponse.to_json())

# convert the object into a dict
v1_list_app_logs_response_dict = v1_list_app_logs_response_instance.to_dict()
# create an instance of V1ListAppLogsResponse from a dict
v1_list_app_logs_response_form_dict = v1_list_app_logs_response.from_dict(v1_list_app_logs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


