# PIWebAsync

*An asynchronous client API for interfacing with OSIsoft [PI Web API](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help.html)*

piwebasync is an HTTP/Websocket client for Python 3 that allows for concurrent requests/streaming to/from a PI Web API server. It is built on top of [Asyncio](https://docs.python.org/3/library/asyncio.html), [Pydantic](https://pydantic-docs.helpmanual.io/), [HTTPX](https://www.python-httpx.org/), and [Websockets](https://websockets.readthedocs.io/en/stable/index.html).

The key features are:

- Fast: Fully asynchronous API and fast JSON normalization 
- Validation: Provides first class objects for constructing PI Web API requests that are validated with Pydantic
- Response Handling: Provides flexibility to user for how to handle API response errors from PI Web API
- Robust: Built on HTTPX and Websockets, two production-ready client libraries
- Authentication Support: Supports Kerberos, NTLM, Bearer, etc. through HTTPX style auth flows in both HTTP and Websocket requests

Install piwebasync using pip:

	pip install piwebasync

And lets get started...
```python
import asyncio
# Using Negotiate auth as an example
from async_negotiate_auth import NegotiateAuth
from piwebasync import Controller, HTTPClient

async def main():
    request = Controller(
        scheme="https",
        host="mypihost.com",
        root="piwebapi"
    ).points.get_by_path("\\\\MyDataserver\\MyPoint")
    async with HTTPClient(auth=NegotiateAuth(), safe_chars='/?:=&%;\\') as client:
        response = await client.get(request)
        print(response.select("WebId", "Name"))

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

For a run through of all the basics head over the [Quick Start](https://github.com/newvicx/piwebasync/blob/main/docs/Quick%20Start.md)

For more advanced topics, see the [Advanced Usage](https://github.com/newvicx/piwebasync/blob/main/docs/Advanced%20Usage.md)

An [API Reference](https://github.com/newvicx/piwebasync/blob/main/docs/API%20Reference.md) page is also provided

## Dependencies

#### Requires

- httpx: Full featured HTTP client, provides backbone for all HTTP requests to PI Web API
- pydantic: Data validation and settings management using python type annotations. Validates API endpoints
- websockets: Websocket client library. Allows support for PI Web API [channels](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/channels.html) to stream data 
- httpx-extensions: An async client built on HTTPX that provides connection management features which allows for Kerberos and NTLM authentication
- ws-auth: A protocol extension for the websockets library which allows the WebsocketClient to support HTTPX-style auth flows

#### Optional Dependencies

- async-negotiate-sspi: Single-Sign On for HTTP and Websocket Negotiate authentication in async frameworks on Windows
- httpx-gssapi: A GSSAPI authentication handler for Python's HTTPX

#### Supports

- Python >= 3.8

## Contributing
If you are interested in contributing to the project, check out the [todo](https://github.com/newvicx/piwebasync/labels/todo) section of the issues page

