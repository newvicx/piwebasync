# piwebasync
An asynchronous python API for making requests to an OSIsoft PI Web API server
## Background
piwebasync is a PI Web API client library built on top of asyncio that supports HTTP and Websocket requests. It supports Kerberos and NTLM authentication.
## Installation
You can install piwebasync via pip

    pip install piwebasync
## Documentation
Coming soon
## Usage
### HTTP
All HTTP methods supported by the PI Web API are supported by piwebasync including GET, POST, PUT, PATCH, and DELETE. The `HTTPClient` class is built on top of [HTTPX](https://www.python-httpx.org/async/) and mimics the `AsyncClient` API closely

    import asyncio
    from piwebasync import HTTPClient
    from piwebasync.api import Streams, HTTPResponse
	
	async def main():
		webid = "SampleWebId"
		resource = Streams.get_end(webid)
		async with HTTPClient(scheme="https", host="myhost", root="/piwebapi") as client:
			response: HTTPResponse = await client.get(resource)
			print(response.Items)
	
	if __name__ == "__main__":
		asyncio.run(main())

### Websockets
The PI Web API has a feature called [Channels](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/channels.html) which use the websocket protocol to continuously stream PI data. piwebasync supports channels through the `Channel` class and has an API that closely mimics the [Websockets](https://websockets.readthedocs.io/en/stable/reference/client.html) client API. Note when using channels you must specify the  scheme, host, and root in the resource definition in order to construct an absolute URL

    import asyncio
    from piwebasync import Channel
    from piwebasync.api import Streams
	
	async def main():
		webid = "SampleWebId"
		resource = Streams.get_channel(webid, scheme="wss", host="myhost", root="/piwebapi")
		async with Channel(resource) as stream:
			async for response in stream:
				print(response.Items)
	
	if __name__ == "__main__":
		asyncio.run(main())
### Authentication
piwebasync supports Kerberos and NTLM authentication via the [async_negotiate_sspi](https://github.com/newvicx/async_negotiate_sspi) package which is installed with piwebasync

    import asyncio
    from async_negotiate_sspi import NegotiateAuthWS
    from piwebasync import Channel
    from piwebasync.api import Streams
	
	async def main():
		webid = "SampleWebId"
		auth = NegotiateAuthWS()
		resource = Streams.get_channel(webid, scheme="wss", host="myhost", root="/piwebapi")
		async with Channel(resource, auth=auth) as stream:
			async for response in stream:
				print(response.Items)
		
	if __name__ == "__main__":
		asyncio.run(main())
## Supports

 - Python >= 3.8
## Requires
 - httpx_extensions >= 0.1.1
 - ws_auth >= 0.0.1
 - async_negotiate_sspi >= 0.1.3
 - pydantic >= 1.9
 - orjson >= 3.6

