# V1Like


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**log_name** | **str** |  | [optional] 
**thumbs_reaction** | [**V1ThumbsReaction**](V1ThumbsReaction.md) |  | [optional] 
**user_id** | **str** |  | [optional] 
**origin** | [**V1OriginType**](V1OriginType.md) |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.v1_like import V1Like

# TODO update the JSON string below
json = "{}"
# create an instance of V1Like from a JSON string
v1_like_instance = V1Like.from_json(json)
# print the JSON string representation of the object
print(V1Like.to_json())

# convert the object into a dict
v1_like_dict = v1_like_instance.to_dict()
# create an instance of V1Like from a dict
v1_like_form_dict = v1_like.from_dict(v1_like_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


