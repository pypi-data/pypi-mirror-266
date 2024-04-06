# V1AttributeFilters


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**keys** | **List[str]** |  | [optional] 
**values** | **List[str]** |  | [optional] 

## Example

```python
from openapi_client.models.v1_attribute_filters import V1AttributeFilters

# TODO update the JSON string below
json = "{}"
# create an instance of V1AttributeFilters from a JSON string
v1_attribute_filters_instance = V1AttributeFilters.from_json(json)
# print the JSON string representation of the object
print(V1AttributeFilters.to_json())

# convert the object into a dict
v1_attribute_filters_dict = v1_attribute_filters_instance.to_dict()
# create an instance of V1AttributeFilters from a dict
v1_attribute_filters_form_dict = v1_attribute_filters.from_dict(v1_attribute_filters_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


