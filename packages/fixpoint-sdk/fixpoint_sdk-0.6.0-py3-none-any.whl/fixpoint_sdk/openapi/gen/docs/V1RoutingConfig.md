# V1RoutingConfig


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**fallback_strategy** | [**V1FallbackStrategy**](V1FallbackStrategy.md) |  | [optional] 
**terminal_state** | [**V1TerminalState**](V1TerminalState.md) |  | [optional] 
**models** | [**List[V1Model]**](V1Model.md) |  | [optional] 
**description** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.v1_routing_config import V1RoutingConfig

# TODO update the JSON string below
json = "{}"
# create an instance of V1RoutingConfig from a JSON string
v1_routing_config_instance = V1RoutingConfig.from_json(json)
# print the JSON string representation of the object
print(V1RoutingConfig.to_json())

# convert the object into a dict
v1_routing_config_dict = v1_routing_config_instance.to_dict()
# create an instance of V1RoutingConfig from a dict
v1_routing_config_form_dict = v1_routing_config.from_dict(v1_routing_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


