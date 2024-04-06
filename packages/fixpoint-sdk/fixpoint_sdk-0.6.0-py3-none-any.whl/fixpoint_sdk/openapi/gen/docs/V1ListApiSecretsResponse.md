# V1ListApiSecretsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_secrets** | [**List[V1ApiSecret]**](V1ApiSecret.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_list_api_secrets_response import V1ListApiSecretsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListApiSecretsResponse from a JSON string
v1_list_api_secrets_response_instance = V1ListApiSecretsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListApiSecretsResponse.to_json())

# convert the object into a dict
v1_list_api_secrets_response_dict = v1_list_api_secrets_response_instance.to_dict()
# create an instance of V1ListApiSecretsResponse from a dict
v1_list_api_secrets_response_form_dict = v1_list_api_secrets_response.from_dict(v1_list_api_secrets_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


