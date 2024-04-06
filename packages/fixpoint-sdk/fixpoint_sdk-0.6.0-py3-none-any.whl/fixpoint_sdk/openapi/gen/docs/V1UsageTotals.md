# V1UsageTotals


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**tokens_used** | **int** |  | [optional] 
**usage_reset_at** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.v1_usage_totals import V1UsageTotals

# TODO update the JSON string below
json = "{}"
# create an instance of V1UsageTotals from a JSON string
v1_usage_totals_instance = V1UsageTotals.from_json(json)
# print the JSON string representation of the object
print(V1UsageTotals.to_json())

# convert the object into a dict
v1_usage_totals_dict = v1_usage_totals_instance.to_dict()
# create an instance of V1UsageTotals from a dict
v1_usage_totals_form_dict = v1_usage_totals.from_dict(v1_usage_totals_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


