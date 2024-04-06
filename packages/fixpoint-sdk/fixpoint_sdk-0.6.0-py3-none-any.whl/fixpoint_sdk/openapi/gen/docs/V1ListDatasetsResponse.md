# V1ListDatasetsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**datasets** | [**List[V1Dataset]**](V1Dataset.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_list_datasets_response import V1ListDatasetsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListDatasetsResponse from a JSON string
v1_list_datasets_response_instance = V1ListDatasetsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListDatasetsResponse.to_json())

# convert the object into a dict
v1_list_datasets_response_dict = v1_list_datasets_response_instance.to_dict()
# create an instance of V1ListDatasetsResponse from a dict
v1_list_datasets_response_form_dict = v1_list_datasets_response.from_dict(v1_list_datasets_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


