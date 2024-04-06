# V1SpendCap


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**reset_interval** | [**V1ResetInterval**](V1ResetInterval.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_spend_cap import V1SpendCap

# TODO update the JSON string below
json = "{}"
# create an instance of V1SpendCap from a JSON string
v1_spend_cap_instance = V1SpendCap.from_json(json)
# print the JSON string representation of the object
print(V1SpendCap.to_json())

# convert the object into a dict
v1_spend_cap_dict = v1_spend_cap_instance.to_dict()
# create an instance of V1SpendCap from a dict
v1_spend_cap_form_dict = v1_spend_cap.from_dict(v1_spend_cap_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


