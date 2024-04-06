# V1CreateApiSecretRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider** | [**V1ApiSecretProvider**](V1ApiSecretProvider.md) |  | [optional] 
**secret** | **str** |  | [optional] 
**alias** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_create_api_secret_request import V1CreateApiSecretRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateApiSecretRequest from a JSON string
v1_create_api_secret_request_instance = V1CreateApiSecretRequest.from_json(json)
# print the JSON string representation of the object
print(V1CreateApiSecretRequest.to_json())

# convert the object into a dict
v1_create_api_secret_request_dict = v1_create_api_secret_request_instance.to_dict()
# create an instance of V1CreateApiSecretRequest from a dict
v1_create_api_secret_request_form_dict = v1_create_api_secret_request.from_dict(v1_create_api_secret_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


