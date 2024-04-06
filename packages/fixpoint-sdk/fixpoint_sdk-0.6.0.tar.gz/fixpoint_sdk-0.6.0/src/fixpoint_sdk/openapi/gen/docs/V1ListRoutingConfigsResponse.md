# V1ListRoutingConfigsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**routing_configs** | [**List[V1RoutingConfig]**](V1RoutingConfig.md) |  | [optional] 
**next_page_token** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_list_routing_configs_response import V1ListRoutingConfigsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListRoutingConfigsResponse from a JSON string
v1_list_routing_configs_response_instance = V1ListRoutingConfigsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListRoutingConfigsResponse.to_json())

# convert the object into a dict
v1_list_routing_configs_response_dict = v1_list_routing_configs_response_instance.to_dict()
# create an instance of V1ListRoutingConfigsResponse from a dict
v1_list_routing_configs_response_form_dict = v1_list_routing_configs_response.from_dict(v1_list_routing_configs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


