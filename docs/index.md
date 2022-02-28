# 																												PIWebAsync

*An asynchronous client API for interfacing with OSIsoft PI Web API*

piwebasync is an HTTP/Websocket client for Python 3 that allows for concurrent requests/streaming to/from a PI Web API server. It is built on top of [Asyncio](https://docs.python.org/3/library/asyncio.html), [Pydantic](https://pydantic-docs.helpmanual.io/), [HTTPX](https://www.python-httpx.org/), and [Websockets](https://websockets.readthedocs.io/en/stable/index.html).

The key features are:

- Fast: Retrieve hundreds of thousands of rows and normalize JSON responses in seconds
- Validation: Provides first class objects for constructing PI Web API requests that are validated with Pydantic
- Response Handling: Provides flexibility to user for how to handle API response errors from PI Web API
- Robust: Built on HTTPX and Websockets, two production-ready client libraries
- Authentication Support: Supports Kerberos, NTLM, Bearer, etc. through HTTPX style auth flows in both HTTP and Websocket requests

Install piwebasync using pip:

`pip install piwebasync`

And lets get started...
`import asyncio`
`from async_negotiate_auth import NegotiateAuth`
`from piwebasync import Controller, HTTPClient`

`async def main():`
	`request = Controller(`
		`scheme="https",`
		`host="mypihost.com",`
		`root="piwebapi"`
	`).points.get_by_path("\\\\MyDataserver\\MyPoint")`
	`async with HTTPClient(auth=NegotiateAuth(), safe_chars='/?:=&%;\\') as client:`
		`response = await client.get(request)`
`print(response.select("Items.Timestamp", "Items.Value"))`

`if __name__ == "__main__":
	asyncio.run(main())`

## Documentation

For a run through of all the basics head over the Quick Start

For more advanced topics, see the Advanced Usage

An API Reference page is also provided

## Dependencies

- httpx: Full featured HTTP client, provides backbone for all HTTP requests to PI Web API
- pydantic: Data validation and settings management using python type annotations. Validates API endpoints
- websockets: Websocket client library. Allows support for PI Web API [channels](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/channels.html) to stream data 
- httpx-extensions: An async client built on HTTPX that provides connection management features which allows for Kerberos and NTLM authentication
- ws-auth: A protocol extension for the websockets library which allows the WebsocketClient to support HTTPX-style auth flows

#### Optional Dependencies

- async-negotiate-sspi: Single-Sign On for HTTP and Websocket Negotiate authentication in async frameworks on Windows
- httpx-gssapi: A GSSAPI authentication handler for Python's HTTPX

## Contributing

piwebasync will handle most but not all of the most common queries used in the PI Web API however, it does not fully implement (and thus validate) the whole PI Web API. The following areas could use some love from the community

- Implementations for all PI Web API controllers
- Templates for request bodies (ex. Creating event frames or PI points)
- Expanded test coverage

If you are interested in contributing to piwebasync feel free to do so