# V1ApiSecret


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alias** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**provider** | [**V1ApiSecretProvider**](V1ApiSecretProvider.md) |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**secret** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_api_secret import V1ApiSecret

# TODO update the JSON string below
json = "{}"
# create an instance of V1ApiSecret from a JSON string
v1_api_secret_instance = V1ApiSecret.from_json(json)
# print the JSON string representation of the object
print(V1ApiSecret.to_json())

# convert the object into a dict
v1_api_secret_dict = v1_api_secret_instance.to_dict()
# create an instance of V1ApiSecret from a dict
v1_api_secret_form_dict = v1_api_secret.from_dict(v1_api_secret_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


