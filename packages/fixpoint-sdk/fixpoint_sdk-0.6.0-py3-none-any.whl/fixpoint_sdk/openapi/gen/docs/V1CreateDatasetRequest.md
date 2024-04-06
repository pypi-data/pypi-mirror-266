# V1CreateDatasetRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**log_ids** | **List[str]** |  | [optional] 
**mode** | [**V1Mode**](V1Mode.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_create_dataset_request import V1CreateDatasetRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateDatasetRequest from a JSON string
v1_create_dataset_request_instance = V1CreateDatasetRequest.from_json(json)
# print the JSON string representation of the object
print(V1CreateDatasetRequest.to_json())

# convert the object into a dict
v1_create_dataset_request_dict = v1_create_dataset_request_instance.to_dict()
# create an instance of V1CreateDatasetRequest from a dict
v1_create_dataset_request_form_dict = v1_create_dataset_request.from_dict(v1_create_dataset_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


