# V1LikeIngest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**log_name** | **str** |  | [optional] 
**thumbs_reaction** | [**V1ThumbsReaction**](V1ThumbsReaction.md) |  | [optional] 
**user_id** | **str** |  | [optional] 
**origin** | [**V1OriginType**](V1OriginType.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_like_ingest import V1LikeIngest

# TODO update the JSON string below
json = "{}"
# create an instance of V1LikeIngest from a JSON string
v1_like_ingest_instance = V1LikeIngest.from_json(json)
# print the JSON string representation of the object
print(V1LikeIngest.to_json())

# convert the object into a dict
v1_like_ingest_dict = v1_like_ingest_instance.to_dict()
# create an instance of V1LikeIngest from a dict
v1_like_ingest_form_dict = v1_like_ingest.from_dict(v1_like_ingest_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


