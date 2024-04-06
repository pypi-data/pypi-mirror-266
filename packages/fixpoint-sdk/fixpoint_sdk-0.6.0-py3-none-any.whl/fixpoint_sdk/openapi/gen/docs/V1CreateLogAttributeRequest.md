# V1CreateLogAttributeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**log_attribute** | [**V1LogAttribute**](V1LogAttribute.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_create_log_attribute_request import V1CreateLogAttributeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateLogAttributeRequest from a JSON string
v1_create_log_attribute_request_instance = V1CreateLogAttributeRequest.from_json(json)
# print the JSON string representation of the object
print(V1CreateLogAttributeRequest.to_json())

# convert the object into a dict
v1_create_log_attribute_request_dict = v1_create_log_attribute_request_instance.to_dict()
# create an instance of V1CreateLogAttributeRequest from a dict
v1_create_log_attribute_request_form_dict = v1_create_log_attribute_request.from_dict(v1_create_log_attribute_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


