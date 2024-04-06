# V1Message


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | **str** |  | [optional] 
**content** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.v1_message import V1Message

# TODO update the JSON string below
json = "{}"
# create an instance of V1Message from a JSON string
v1_message_instance = V1Message.from_json(json)
# print the JSON string representation of the object
print(V1Message.to_json())

# convert the object into a dict
v1_message_dict = v1_message_instance.to_dict()
# create an instance of V1Message from a dict
v1_message_form_dict = v1_message.from_dict(v1_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


