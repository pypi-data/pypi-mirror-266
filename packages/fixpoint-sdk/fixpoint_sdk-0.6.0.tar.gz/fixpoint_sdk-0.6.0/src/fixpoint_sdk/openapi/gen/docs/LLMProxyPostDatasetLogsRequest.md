# LLMProxyPostDatasetLogsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**log_names** | **List[str]** |  | [optional] 

## Example

```python
from openapi_client.models.llm_proxy_post_dataset_logs_request import LLMProxyPostDatasetLogsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMProxyPostDatasetLogsRequest from a JSON string
llm_proxy_post_dataset_logs_request_instance = LLMProxyPostDatasetLogsRequest.from_json(json)
# print the JSON string representation of the object
print(LLMProxyPostDatasetLogsRequest.to_json())

# convert the object into a dict
llm_proxy_post_dataset_logs_request_dict = llm_proxy_post_dataset_logs_request_instance.to_dict()
# create an instance of LLMProxyPostDatasetLogsRequest from a dict
llm_proxy_post_dataset_logs_request_form_dict = llm_proxy_post_dataset_logs_request.from_dict(llm_proxy_post_dataset_logs_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


