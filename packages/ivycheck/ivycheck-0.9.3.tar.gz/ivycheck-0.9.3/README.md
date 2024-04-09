# IvyCheck-SDK

<div align="left">
    <a href="https://speakeasyapi.dev/"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<!-- Start SDK Installation [installation] -->
## SDK Installation

```bash
pip install ivycheck
```
<!-- End SDK Installation [installation] -->

## SDK Example Usage

### Example

```python
import ivycheck

ivy = ivycheck.IvyCheck(
    api_key="<YOUR_TOKEN_HERE>",
)

res = ivy.checks.hallucination(response="It is sunny outside", context="It is rainig cats and dogs")
# CheckResult(passed=False, score=0.9992709300131537, message='Hallucination detected')

```

<!-- No SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

### [checks](docs/sdks/checks/README.md)

* [hallucination](docs/sdks/checks/README.md#hallucination) - Hallucination
* [pii](docs/sdks/checks/README.md#pii) - Pii
* [prompt_injection](docs/sdks/checks/README.md#prompt_injection) - Prompt Injection
<!-- End Available Resources and Operations [operations] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations.  All operations return a response object or raise an error.  If Error objects are specified in your OpenAPI Spec, the SDK will raise the appropriate Error type.

| Error Object               | Status Code                | Content Type               |
| -------------------------- | -------------------------- | -------------------------- |
| models.HTTPValidationError | 422                        | application/json           |
| models.SDKError            | 4xx-5xx                    | */*                        |

### Example

```python
import ivycheck
from ivycheck import models

s = ivycheck.IvyCheck(
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = None
try:
    res = s.checks.hallucination(response='<value>', context='<value>', project_id='<value>')
except models.HTTPValidationError as e:
    # handle exception
    raise(e)
except models.SDKError as e:
    # handle exception
    raise(e)

if res.check_result is not None:
    # handle response
    pass

```
<!-- End Error Handling [errors] -->
<!-- No Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [requests](https://pypi.org/project/requests/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with a custom `requests.Session` object.

For example, you could specify a header for every request that this sdk makes as follows:
```python
import ivycheck
import requests

http_client = requests.Session()
http_client.headers.update({'x-custom-header': 'someValue'})
s = ivycheck.IvyCheck(client=http_client)
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name        | Type        | Scheme      |
| ----------- | ----------- | ----------- |
| `api_key`   | http        | HTTP Bearer |

To authenticate with the API the `api_key` parameter must be set when initializing the SDK client instance. For example:
```python
import ivycheck

s = ivycheck.IvyCheck(
    api_key="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.checks.hallucination(response='<value>', context='<value>', project_id='<value>')

if res.check_result is not None:
    # handle response
    pass

```
<!-- End Authentication [security] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically.
Feel free to open a PR or a Github issue as a proof of concept and we'll do our best to include it in a future release!

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
