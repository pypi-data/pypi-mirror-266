# openapi_client.LLMProxyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**l_lm_proxy_create_api_secret**](LLMProxyApi.md#l_lm_proxy_create_api_secret) | **POST** /v1/api_secrets | Store LLM inference API secret
[**l_lm_proxy_create_app_logs**](LLMProxyApi.md#l_lm_proxy_create_app_logs) | **POST** /v1/app_logs | Create application logs
[**l_lm_proxy_create_dataset**](LLMProxyApi.md#l_lm_proxy_create_dataset) | **POST** /v1/datasets | Create LLM dataset
[**l_lm_proxy_create_likes**](LLMProxyApi.md#l_lm_proxy_create_likes) | **POST** /v1/likes | Add LLM log feedback (\&quot;likes\&quot;)
[**l_lm_proxy_create_log_attribute**](LLMProxyApi.md#l_lm_proxy_create_log_attribute) | **POST** /v1/attributes | Attach attribute to LLM log
[**l_lm_proxy_create_open_ai_chat_input_log**](LLMProxyApi.md#l_lm_proxy_create_open_ai_chat_input_log) | **POST** /v1/openai_chats/{modelName}/input_logs | Create an LLM input log
[**l_lm_proxy_create_open_ai_chat_output_log**](LLMProxyApi.md#l_lm_proxy_create_open_ai_chat_output_log) | **POST** /v1/openai_chats/{modelName}/output_logs | Create an LLM output log
[**l_lm_proxy_create_routing_config**](LLMProxyApi.md#l_lm_proxy_create_routing_config) | **POST** /v1/routing_configs | Create LLM routing config
[**l_lm_proxy_delete_log_attribute**](LLMProxyApi.md#l_lm_proxy_delete_log_attribute) | **DELETE** /v1/attributes/{name} | Remove LLM log attribute
[**l_lm_proxy_list_api_secrets**](LLMProxyApi.md#l_lm_proxy_list_api_secrets) | **GET** /v1/api_secrets | List LLM inference API secrets
[**l_lm_proxy_list_app_logs**](LLMProxyApi.md#l_lm_proxy_list_app_logs) | **GET** /v1/app_logs | List application logs
[**l_lm_proxy_list_datasets**](LLMProxyApi.md#l_lm_proxy_list_datasets) | **GET** /v1/datasets | List LLM datasets
[**l_lm_proxy_list_likes**](LLMProxyApi.md#l_lm_proxy_list_likes) | **GET** /v1/likes | List LLM log feedback (\&quot;likes\&quot;)
[**l_lm_proxy_list_log_attributes**](LLMProxyApi.md#l_lm_proxy_list_log_attributes) | **GET** /v1/attributes | List attributes on an LLM log
[**l_lm_proxy_list_open_ai_chat_logs**](LLMProxyApi.md#l_lm_proxy_list_open_ai_chat_logs) | **GET** /v1/{parent}/logs | List LLM logs
[**l_lm_proxy_list_routing_configs**](LLMProxyApi.md#l_lm_proxy_list_routing_configs) | **GET** /v1/routing_configs | List LLM routing configs
[**l_lm_proxy_post_dataset_logs**](LLMProxyApi.md#l_lm_proxy_post_dataset_logs) | **POST** /v1/datasets/{name}/logs | Add logs to a dataset
[**l_lm_proxy_update_spending_totals**](LLMProxyApi.md#l_lm_proxy_update_spending_totals) | **PATCH** /v1/routing_configs/{routeConfigId} | Update routing config spending totals


# **l_lm_proxy_create_api_secret**
> V1ApiSecret l_lm_proxy_create_api_secret(body)

Store LLM inference API secret

This lets Fixpoint make select inference interactions on your behalf, such as running a fine-tuning operation or running LLM evaluations on monitored LLM logs.

### Example


```python
import openapi_client
from openapi_client.models.v1_api_secret import V1ApiSecret
from openapi_client.models.v1_create_api_secret_request import V1CreateApiSecretRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    body = openapi_client.V1CreateApiSecretRequest() # V1CreateApiSecretRequest | 

    try:
        # Store LLM inference API secret
        api_response = api_instance.l_lm_proxy_create_api_secret(body)
        print("The response of LLMProxyApi->l_lm_proxy_create_api_secret:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_api_secret: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateApiSecretRequest**](V1CreateApiSecretRequest.md)|  | 

### Return type

[**V1ApiSecret**](V1ApiSecret.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_app_logs**
> V1CreateAppLogsResponse l_lm_proxy_create_app_logs(body)

Create application logs

Create 1 or more application logs, which you can attach to an LLM log via a trace_id. This is useful when you want to see what was going on in the rest of your application when an LLM inference request was made.

### Example


```python
import openapi_client
from openapi_client.models.v1_create_app_logs_request import V1CreateAppLogsRequest
from openapi_client.models.v1_create_app_logs_response import V1CreateAppLogsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    body = openapi_client.V1CreateAppLogsRequest() # V1CreateAppLogsRequest | 

    try:
        # Create application logs
        api_response = api_instance.l_lm_proxy_create_app_logs(body)
        print("The response of LLMProxyApi->l_lm_proxy_create_app_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_app_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateAppLogsRequest**](V1CreateAppLogsRequest.md)|  | 

### Return type

[**V1CreateAppLogsResponse**](V1CreateAppLogsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_dataset**
> V1CreateDatasetResponse l_lm_proxy_create_dataset(body)

Create LLM dataset

### Example


```python
import openapi_client
from openapi_client.models.v1_create_dataset_request import V1CreateDatasetRequest
from openapi_client.models.v1_create_dataset_response import V1CreateDatasetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    body = openapi_client.V1CreateDatasetRequest() # V1CreateDatasetRequest | 

    try:
        # Create LLM dataset
        api_response = api_instance.l_lm_proxy_create_dataset(body)
        print("The response of LLMProxyApi->l_lm_proxy_create_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateDatasetRequest**](V1CreateDatasetRequest.md)|  | 

### Return type

[**V1CreateDatasetResponse**](V1CreateDatasetResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_likes**
> V1CreateLikesResponse l_lm_proxy_create_likes(body)

Add LLM log feedback (\"likes\")

Create \"likes\" or user feedback for an LLM log. The user feedback can be from an internal user (such as LL prompt engineer) or an external end-user.

### Example


```python
import openapi_client
from openapi_client.models.v1_create_likes_request import V1CreateLikesRequest
from openapi_client.models.v1_create_likes_response import V1CreateLikesResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    body = openapi_client.V1CreateLikesRequest() # V1CreateLikesRequest | 

    try:
        # Add LLM log feedback (\"likes\")
        api_response = api_instance.l_lm_proxy_create_likes(body)
        print("The response of LLMProxyApi->l_lm_proxy_create_likes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_likes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateLikesRequest**](V1CreateLikesRequest.md)|  | 

### Return type

[**V1CreateLikesResponse**](V1CreateLikesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_log_attribute**
> V1CreateLogAttributeResponse l_lm_proxy_create_log_attribute(body)

Attach attribute to LLM log

### Example


```python
import openapi_client
from openapi_client.models.v1_create_log_attribute_request import V1CreateLogAttributeRequest
from openapi_client.models.v1_create_log_attribute_response import V1CreateLogAttributeResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    body = openapi_client.V1CreateLogAttributeRequest() # V1CreateLogAttributeRequest | 

    try:
        # Attach attribute to LLM log
        api_response = api_instance.l_lm_proxy_create_log_attribute(body)
        print("The response of LLMProxyApi->l_lm_proxy_create_log_attribute:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_log_attribute: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateLogAttributeRequest**](V1CreateLogAttributeRequest.md)|  | 

### Return type

[**V1CreateLogAttributeResponse**](V1CreateLogAttributeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_open_ai_chat_input_log**
> V1OpenAIChatInputLog l_lm_proxy_create_open_ai_chat_input_log(model_name, body)

Create an LLM input log

Store an LLM inference request's input in Fixpoint (aka the \"LLM input log\").

### Example


```python
import openapi_client
from openapi_client.models.llm_proxy_create_open_ai_chat_input_log_request import LLMProxyCreateOpenAIChatInputLogRequest
from openapi_client.models.v1_open_ai_chat_input_log import V1OpenAIChatInputLog
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    model_name = 'model_name_example' # str | 
    body = openapi_client.LLMProxyCreateOpenAIChatInputLogRequest() # LLMProxyCreateOpenAIChatInputLogRequest | 

    try:
        # Create an LLM input log
        api_response = api_instance.l_lm_proxy_create_open_ai_chat_input_log(model_name, body)
        print("The response of LLMProxyApi->l_lm_proxy_create_open_ai_chat_input_log:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_open_ai_chat_input_log: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_name** | **str**|  | 
 **body** | [**LLMProxyCreateOpenAIChatInputLogRequest**](LLMProxyCreateOpenAIChatInputLogRequest.md)|  | 

### Return type

[**V1OpenAIChatInputLog**](V1OpenAIChatInputLog.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_open_ai_chat_output_log**
> V1OpenAIChatOutputLog l_lm_proxy_create_open_ai_chat_output_log(model_name, body)

Create an LLM output log

Store an LLM inference request's output in Fixpoint (aka the \"LLM output log\").

### Example


```python
import openapi_client
from openapi_client.models.llm_proxy_create_open_ai_chat_output_log_request import LLMProxyCreateOpenAIChatOutputLogRequest
from openapi_client.models.v1_open_ai_chat_output_log import V1OpenAIChatOutputLog
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    model_name = 'model_name_example' # str | 
    body = openapi_client.LLMProxyCreateOpenAIChatOutputLogRequest() # LLMProxyCreateOpenAIChatOutputLogRequest | 

    try:
        # Create an LLM output log
        api_response = api_instance.l_lm_proxy_create_open_ai_chat_output_log(model_name, body)
        print("The response of LLMProxyApi->l_lm_proxy_create_open_ai_chat_output_log:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_open_ai_chat_output_log: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_name** | **str**|  | 
 **body** | [**LLMProxyCreateOpenAIChatOutputLogRequest**](LLMProxyCreateOpenAIChatOutputLogRequest.md)|  | 

### Return type

[**V1OpenAIChatOutputLog**](V1OpenAIChatOutputLog.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_create_routing_config**
> V1RoutingConfig l_lm_proxy_create_routing_config(body)

Create LLM routing config

Creates an LLM inference routing config so you can dynamically control to which LLM models or inference providers Fixpoint sends LLM inference requests.  Routing configs can:  - Have configurable spending caps per model

### Example


```python
import openapi_client
from openapi_client.models.v1_create_routing_config_request import V1CreateRoutingConfigRequest
from openapi_client.models.v1_routing_config import V1RoutingConfig
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    body = openapi_client.V1CreateRoutingConfigRequest() # V1CreateRoutingConfigRequest | 

    try:
        # Create LLM routing config
        api_response = api_instance.l_lm_proxy_create_routing_config(body)
        print("The response of LLMProxyApi->l_lm_proxy_create_routing_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_create_routing_config: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateRoutingConfigRequest**](V1CreateRoutingConfigRequest.md)|  | 

### Return type

[**V1RoutingConfig**](V1RoutingConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_delete_log_attribute**
> V1DeleteLogAttributeResponse l_lm_proxy_delete_log_attribute(name)

Remove LLM log attribute

### Example


```python
import openapi_client
from openapi_client.models.v1_delete_log_attribute_response import V1DeleteLogAttributeResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    name = 'name_example' # str | 

    try:
        # Remove LLM log attribute
        api_response = api_instance.l_lm_proxy_delete_log_attribute(name)
        print("The response of LLMProxyApi->l_lm_proxy_delete_log_attribute:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_delete_log_attribute: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**V1DeleteLogAttributeResponse**](V1DeleteLogAttributeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_api_secrets**
> V1ListApiSecretsResponse l_lm_proxy_list_api_secrets()

List LLM inference API secrets

### Example


```python
import openapi_client
from openapi_client.models.v1_list_api_secrets_response import V1ListApiSecretsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)

    try:
        # List LLM inference API secrets
        api_response = api_instance.l_lm_proxy_list_api_secrets()
        print("The response of LLMProxyApi->l_lm_proxy_list_api_secrets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_api_secrets: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1ListApiSecretsResponse**](V1ListApiSecretsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_app_logs**
> V1ListAppLogsResponse l_lm_proxy_list_app_logs(trace_id=trace_id)

List application logs

List application logs stored in Fixpoint.

### Example


```python
import openapi_client
from openapi_client.models.v1_list_app_logs_response import V1ListAppLogsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    trace_id = 'trace_id_example' # str |  (optional)

    try:
        # List application logs
        api_response = api_instance.l_lm_proxy_list_app_logs(trace_id=trace_id)
        print("The response of LLMProxyApi->l_lm_proxy_list_app_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_app_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trace_id** | **str**|  | [optional] 

### Return type

[**V1ListAppLogsResponse**](V1ListAppLogsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_datasets**
> V1ListDatasetsResponse l_lm_proxy_list_datasets(dataset_name=dataset_name, mode=mode)

List LLM datasets

### Example


```python
import openapi_client
from openapi_client.models.v1_list_datasets_response import V1ListDatasetsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    dataset_name = 'dataset_name_example' # str |  (optional)
    mode = 'MODE_UNSPECIFIED' # str |  (optional) (default to 'MODE_UNSPECIFIED')

    try:
        # List LLM datasets
        api_response = api_instance.l_lm_proxy_list_datasets(dataset_name=dataset_name, mode=mode)
        print("The response of LLMProxyApi->l_lm_proxy_list_datasets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_name** | **str**|  | [optional] 
 **mode** | **str**|  | [optional] [default to &#39;MODE_UNSPECIFIED&#39;]

### Return type

[**V1ListDatasetsResponse**](V1ListDatasetsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_likes**
> V1ListLikesResponse l_lm_proxy_list_likes(page_size=page_size, log_name=log_name, user_id=user_id, origin=origin, thumbs_reaction=thumbs_reaction)

List LLM log feedback (\"likes\")

### Example


```python
import openapi_client
from openapi_client.models.v1_list_likes_response import V1ListLikesResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    page_size = 56 # int |  (optional)
    log_name = 'log_name_example' # str |  (optional)
    user_id = 'user_id_example' # str |  (optional)
    origin = 'ORIGIN_UNSPECIFIED' # str |  (optional) (default to 'ORIGIN_UNSPECIFIED')
    thumbs_reaction = 'THUMBS_UNSPECIFIED' # str |  (optional) (default to 'THUMBS_UNSPECIFIED')

    try:
        # List LLM log feedback (\"likes\")
        api_response = api_instance.l_lm_proxy_list_likes(page_size=page_size, log_name=log_name, user_id=user_id, origin=origin, thumbs_reaction=thumbs_reaction)
        print("The response of LLMProxyApi->l_lm_proxy_list_likes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_likes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | [optional] 
 **log_name** | **str**|  | [optional] 
 **user_id** | **str**|  | [optional] 
 **origin** | **str**|  | [optional] [default to &#39;ORIGIN_UNSPECIFIED&#39;]
 **thumbs_reaction** | **str**|  | [optional] [default to &#39;THUMBS_UNSPECIFIED&#39;]

### Return type

[**V1ListLikesResponse**](V1ListLikesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_log_attributes**
> V1ListLogAttributesResponse l_lm_proxy_list_log_attributes(log_name=log_name)

List attributes on an LLM log

### Example


```python
import openapi_client
from openapi_client.models.v1_list_log_attributes_response import V1ListLogAttributesResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    log_name = 'log_name_example' # str |  (optional)

    try:
        # List attributes on an LLM log
        api_response = api_instance.l_lm_proxy_list_log_attributes(log_name=log_name)
        print("The response of LLMProxyApi->l_lm_proxy_list_log_attributes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_log_attributes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **log_name** | **str**|  | [optional] 

### Return type

[**V1ListLogAttributesResponse**](V1ListLogAttributesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_open_ai_chat_logs**
> V1ListOpenAIChatLogsResponse l_lm_proxy_list_open_ai_chat_logs(parent, page_size=page_size, page_token=page_token, filters_relative_datetime_filters_from_s=filters_relative_datetime_filters_from_s, filters_userfeedback_filter_thumbs_reaction=filters_userfeedback_filter_thumbs_reaction, filters_attribute_filters_keys=filters_attribute_filters_keys, filters_attribute_filters_values=filters_attribute_filters_values, filters_dataset_filters_dataset_names=filters_dataset_filters_dataset_names, mode=mode, count_entries=count_entries)

List LLM logs

### Example


```python
import openapi_client
from openapi_client.models.v1_list_open_ai_chat_logs_response import V1ListOpenAIChatLogsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    parent = 'parent_example' # str | The parent resource collection. In this case, \"/openai_chats/{model_name}\".
    page_size = 56 # int |  (optional)
    page_token = 'page_token_example' # str |  (optional)
    filters_relative_datetime_filters_from_s = 'filters_relative_datetime_filters_from_s_example' # str | Number of seconds from current datetime (optional)
    filters_userfeedback_filter_thumbs_reaction = 'THUMBS_UNSPECIFIED' # str |  (optional) (default to 'THUMBS_UNSPECIFIED')
    filters_attribute_filters_keys = ['filters_attribute_filters_keys_example'] # List[str] |  (optional)
    filters_attribute_filters_values = ['filters_attribute_filters_values_example'] # List[str] |  (optional)
    filters_dataset_filters_dataset_names = ['filters_dataset_filters_dataset_names_example'] # List[str] |  (optional)
    mode = 'MODE_UNSPECIFIED' # str |  (optional) (default to 'MODE_UNSPECIFIED')
    count_entries = True # bool | Whether to also return a count of all the entries matching the list query. (optional)

    try:
        # List LLM logs
        api_response = api_instance.l_lm_proxy_list_open_ai_chat_logs(parent, page_size=page_size, page_token=page_token, filters_relative_datetime_filters_from_s=filters_relative_datetime_filters_from_s, filters_userfeedback_filter_thumbs_reaction=filters_userfeedback_filter_thumbs_reaction, filters_attribute_filters_keys=filters_attribute_filters_keys, filters_attribute_filters_values=filters_attribute_filters_values, filters_dataset_filters_dataset_names=filters_dataset_filters_dataset_names, mode=mode, count_entries=count_entries)
        print("The response of LLMProxyApi->l_lm_proxy_list_open_ai_chat_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_open_ai_chat_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| The parent resource collection. In this case, \&quot;/openai_chats/{model_name}\&quot;. | 
 **page_size** | **int**|  | [optional] 
 **page_token** | **str**|  | [optional] 
 **filters_relative_datetime_filters_from_s** | **str**| Number of seconds from current datetime | [optional] 
 **filters_userfeedback_filter_thumbs_reaction** | **str**|  | [optional] [default to &#39;THUMBS_UNSPECIFIED&#39;]
 **filters_attribute_filters_keys** | [**List[str]**](str.md)|  | [optional] 
 **filters_attribute_filters_values** | [**List[str]**](str.md)|  | [optional] 
 **filters_dataset_filters_dataset_names** | [**List[str]**](str.md)|  | [optional] 
 **mode** | **str**|  | [optional] [default to &#39;MODE_UNSPECIFIED&#39;]
 **count_entries** | **bool**| Whether to also return a count of all the entries matching the list query. | [optional] 

### Return type

[**V1ListOpenAIChatLogsResponse**](V1ListOpenAIChatLogsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_list_routing_configs**
> V1ListRoutingConfigsResponse l_lm_proxy_list_routing_configs()

List LLM routing configs

### Example


```python
import openapi_client
from openapi_client.models.v1_list_routing_configs_response import V1ListRoutingConfigsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)

    try:
        # List LLM routing configs
        api_response = api_instance.l_lm_proxy_list_routing_configs()
        print("The response of LLMProxyApi->l_lm_proxy_list_routing_configs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_list_routing_configs: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1ListRoutingConfigsResponse**](V1ListRoutingConfigsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_post_dataset_logs**
> V1PostDatasetLogsResponse l_lm_proxy_post_dataset_logs(name, body)

Add logs to a dataset

### Example


```python
import openapi_client
from openapi_client.models.llm_proxy_post_dataset_logs_request import LLMProxyPostDatasetLogsRequest
from openapi_client.models.v1_post_dataset_logs_response import V1PostDatasetLogsResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    name = 'name_example' # str | 
    body = openapi_client.LLMProxyPostDatasetLogsRequest() # LLMProxyPostDatasetLogsRequest | 

    try:
        # Add logs to a dataset
        api_response = api_instance.l_lm_proxy_post_dataset_logs(name, body)
        print("The response of LLMProxyApi->l_lm_proxy_post_dataset_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_post_dataset_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **body** | [**LLMProxyPostDatasetLogsRequest**](LLMProxyPostDatasetLogsRequest.md)|  | 

### Return type

[**V1PostDatasetLogsResponse**](V1PostDatasetLogsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **l_lm_proxy_update_spending_totals**
> V1RoutingConfig l_lm_proxy_update_spending_totals(route_config_id, body)

Update routing config spending totals

Update spending totals on a routing config.

### Example


```python
import openapi_client
from openapi_client.models.llm_proxy_update_spending_totals_request import LLMProxyUpdateSpendingTotalsRequest
from openapi_client.models.v1_routing_config import V1RoutingConfig
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.LLMProxyApi(api_client)
    route_config_id = 'route_config_id_example' # str | 
    body = openapi_client.LLMProxyUpdateSpendingTotalsRequest() # LLMProxyUpdateSpendingTotalsRequest | 

    try:
        # Update routing config spending totals
        api_response = api_instance.l_lm_proxy_update_spending_totals(route_config_id, body)
        print("The response of LLMProxyApi->l_lm_proxy_update_spending_totals:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LLMProxyApi->l_lm_proxy_update_spending_totals: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **route_config_id** | **str**|  | 
 **body** | [**LLMProxyUpdateSpendingTotalsRequest**](LLMProxyUpdateSpendingTotalsRequest.md)|  | 

### Return type

[**V1RoutingConfig**](V1RoutingConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

