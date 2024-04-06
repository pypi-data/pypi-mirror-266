# V1ListLikesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**likes** | [**List[V1Like]**](V1Like.md) |  | [optional] 

## Example

```python
from openapi_client.models.v1_list_likes_response import V1ListLikesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListLikesResponse from a JSON string
v1_list_likes_response_instance = V1ListLikesResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListLikesResponse.to_json())

# convert the object into a dict
v1_list_likes_response_dict = v1_list_likes_response_instance.to_dict()
# create an instance of V1ListLikesResponse from a dict
v1_list_likes_response_form_dict = v1_list_likes_response.from_dict(v1_list_likes_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


