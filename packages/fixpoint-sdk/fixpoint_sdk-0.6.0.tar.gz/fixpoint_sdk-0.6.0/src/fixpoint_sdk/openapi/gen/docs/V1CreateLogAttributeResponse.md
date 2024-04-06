# V1CreateLogAttributeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**log_attribute** | [**V1LogAttribute**](V1LogAttribute.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_create_log_attribute_response import V1CreateLogAttributeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateLogAttributeResponse from a JSON string
v1_create_log_attribute_response_instance = V1CreateLogAttributeResponse.from_json(json)
# print the JSON string representation of the object
print(V1CreateLogAttributeResponse.to_json())

# convert the object into a dict
v1_create_log_attribute_response_dict = v1_create_log_attribute_response_instance.to_dict()
# create an instance of V1CreateLogAttributeResponse from a dict
v1_create_log_attribute_response_form_dict = v1_create_log_attribute_response.from_dict(v1_create_log_attribute_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


