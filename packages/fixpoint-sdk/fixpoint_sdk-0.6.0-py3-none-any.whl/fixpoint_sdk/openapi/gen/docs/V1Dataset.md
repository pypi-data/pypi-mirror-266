# V1Dataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**display_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.v1_dataset import V1Dataset

# TODO update the JSON string below
json = "{}"
# create an instance of V1Dataset from a JSON string
v1_dataset_instance = V1Dataset.from_json(json)
# print the JSON string representation of the object
print(V1Dataset.to_json())

# convert the object into a dict
v1_dataset_dict = v1_dataset_instance.to_dict()
# create an instance of V1Dataset from a dict
v1_dataset_form_dict = v1_dataset.from_dict(v1_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


