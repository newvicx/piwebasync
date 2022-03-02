# Quick Start

## Basics

Start by importing piwebasync...

```python
import piwebasync
```

Create a request...
```python
request = piwebasync.Controller(scheme="https",host="myhost.com", root="piwebapi").streams.get_end("point_webid")
```

Make the request...
```python
async with piwebasync.HTTPClient() as client:
	response = await client.request(request)
```

The `HTTPClient` supports all HTTP methods that the PI Web API does including; GET, POST, PUT, PATCH, and DELETE

***Note: Not all controllers nor all controller methods have been implemented in piwebasync (yet!). While the HTTPClient does support all the aforementioned HTTP methods you may need to construct the URL yourself rather than using the Controller class as shown above***

For opening a websocket connection, use the `WebsocketClient`...
```python
request = piwebasync.Controller(scheme="wss",host="myhost.com", root="piwebapi").streams.get_channel("point_webid")

async with piwebasync.WebsocketClient(request) as client:
	async for message in client:
		print("Got a message")
```

## Constructing Requests

The `Controller` class is the base class for constructing all API requests. It provides a structured and validated API for deriving endpoint URL's. A PI Web API request URL has the following structure

	{scheme}://{host}:{port}/{root}/{controller}/{webid}/{action}/{additional path params}?{query params}

### Simple Request

All supported PI Web API controllers can be directly accessed as properties of the Controller class, and all supported actions are functions of that controller. For example, the [Stream](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream.html) controller has the [GetEnd](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getend.html) method. Constructing request for that method in piwebasync would look something like this...

```python
request = Controller(scheme="https",host="myhost.com", root="piwebapi").streams.get_end("point_webid")
```

This returns an `APIRequest` which can be passed directly into an `HTTPClient` instance. The above is equivalent to the URL...

	https://myhost.com/piwebapi/streams/point_webid/end

Which can be verified by accessing the `.absolute_url` attribute of the request

```
>>>request.absolute_url
>>>https://myhost.com/piwebapi/streams/point_webid/end
```

The advantage to using a Controller instance is that all supported methods are validated and type hinted. You can pass native python types in native python syntax and the URL construction will be handled automatically. For simple URLs such as the GetEnd example above this may not seem like a huge deal but lets lets take a more complex example...

### More Complex Request

The [StreamSet](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset.html) controller has an analogous [GetEndAdHoc](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getendadhoc.html) method which allows you to query for multiple PI points in a single request. You can request multiple WebId's by specifying the "webId" parameter multiple times. For example...

	https://myhost.com/piwebapi/streamsets/end?webId=point_1_webid&webId=point_2_webid

Lets add in some selected fields for fun...

	https://myhost.com/piwebapi/streamsets/end?webId=point_1_webid&webId=point_2_webid&selectedFields=Items.WebId;Items.Items.Timestamp;Items.Items.Value

While this isn't out of hand yet imagine constructing a URL with 50 webid's and other query parameters, constructing these URL's can become laborious and error prone. Instead, lets look at how we can construct this endpoint in piwebasync...
```python
request = Controller(
	scheme="https",
	host="myhost.com",
	root="piwebapi"
).streamsets.get_end(
	webid=["point_1_webid", "point_2_webid"],
	selected_fields=["Items.WebId", "Items.Items.Timestamp", "Items.Items.Value"]
)
```

piwebasync will handle all the query parameter formatting including, converting parameters to lower camel case format, adding a semi colon between each selected field, and specifying "webId" for each webid in the list. You can view the formatted URL by accessing the `.absolute_url` attribute
```
>>>request.absolute_url
>>>https://myhost.com/piwebapi/streamsets/end?webId=point_1_webid&webId=point_2_webid&selectedFields=Items.WebId;Items.Items.Timestamp;Items.Items.Value
```

Lastly, all controller methods such as the `.get_end()` method will not accept any parameters not supported by the PI Web API so you can be sure that any URL  will have valid query parameters.

## Sending HTTP Requests

Almost all methods in PI Web API happen over HTTP with the lone exception being the [GetChannel](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getchannel.html) method for both the Stream and StreamSet controllers which use the Websocket protocol. piwebasync provides an `HTTPClient` for handling HTTP requests concurrently.

The preferred way of using the `HTTPClient` is as an async context manager...
```python
async with HTTPClient() as client:
	response = await client.request(request)
```

### Client Configuration

Under the hood, piwebasync uses the `ExClient` from [httpx_extensions](https://github.com/newvicx/httpx_extensions) as the transport for HTTP requests. This client provides easy support for Kerberos and NTLM authentication but it also supports all existing [HTTPX auth flows](https://www.python-httpx.org/advanced/#customizing-authentication). The `HTTPClient` is essentially a simple wrapper around the `ExClient` and just about every parameter in the `HTTPClient` constructor is passed directly into the `ExClient` constructor. You can visit the [API Reference](https://github.com/newvicx/piwebasync/blob/main/docs/API%20Reference.md) to see each parameter used in the `HTTPClient`

Because the `HTTPClient` wraps the the `ExClient` which has an identical API to the `AsyncClient` from HTTPX. The [docs](https://www.python-httpx.org/async/) from HTTPX have a lot of applicable concepts to configuring the client and sending requests

### Responses

Requests return an instance of `HTTPResponse` which has 3 default properties...

> **status_code** (*int*): status code returned from server
> 
> **url** (*str*): request URL that produced response
> 
> **headers** (*httpx.Headers*): response headers from server

Additionally you can access the content of the response body by calling the `.dict()` method. This will return the JSON response body as a dictionary. Alternatively, the top level parameters of the response are also attributes of the response so you can access them via dot notation. For example, consider the example response content...
```json
{
"WebId": "I1DPa70Wf0zBA06CLkV9ovNQgQCAAAAA",
"Id": 82,
"Name": "PointName",
"Path": "\\\\MyPIServer\\PointName",
"Descriptor": "12 Hour Sine Wave",
"PointClass": "classic",
"PointType": "Float32",
"DigitalSetName": "",
"Span": 100.0,
"Zero": 0.0,
"EngineeringUnits": "",
"Step": false,
"Future": false,
"DisplayDigits": -5,
"Links": {
	"Self":
	"https://localhost.osisoft.int/piwebapi/points/I1DPa70Wf0zBA06CLkV9ovNQgQCAAAAA"
}
}
```

All the parameters of the in above response are in the top level of the response body except for "Self" which is nested in "Links". So for example you can access "EngineeringUnits" directly from the `HTTPResponse` object like so...

	response.engineering_units

For selecting values in a response and normalizing the content in deeply nested JSON responses, see the [Advanced Usage](https://github.com/newvicx/piwebasync/blob/main/docs/Advanced%20Usage.md) section

For response handling, particularly when it comes to errors in the response see the [Advanced Usage](https://github.com/newvicx/piwebasync/blob/main/docs/Advanced%20Usage.md) section

### Specifying SafeChars

Oftentimes, characters in requests are not URL safe such as "\\", "%", etc. These characters are usually percent encoded to their URL safe equivalents. The PI Web API says that [all appropriate characters should be percent encoded](https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/url-encoding.html), but in practice, I have found some situations where percent encoding has led to errors in responses. For these situations you can specify `safe_chars` as a string of characters which will not be encoded and instead sent as is.

For example, take the following URL...

	https://pivision.com/piwebapi/points/?path=\\MyPIServer\PointName

HTTPX and by extension, the `ExClient` would encode and attempt to reach the following URL...

	https://pivision.com/piwebapi/points/?path=%2F%2FMyPIServer%2FPointName

This will lead to an error in the PI Web API (Tested on PI Web API 2019 SP1)
```json
{
"Errors": [
	"The specified path was not found. If more details are needed, please contact your PI Web API administrator for help in enabling debug mode."
	]
}
```

To fix this you can specify the `safe_chars` parameter in the `HTTPClient` constructor...
```python
client = HTTPClient(safe_chars='/:?=\\')
```

***Note: You need to include all characters that have a percent encoding when specifying `safe_chars` even if these characters would not have been percent encoded previously. For example you can see how "/", "?", ":" and "=" are included as `safe_chars` even though they weren't percent encoded before***

## Websockets (Channels)

A channel is a way to receive continuous updates about a stream or stream set. Rather than using a typical HTTP request, channels are accessed using the Websocket protocol

The preferred way of using the `WebsocketClient` is as an async context manager...

```python
async with WebsocketClient(request) as channel:
	message = await channel.recv()
```

### Client Configuration

Under the hood, piwebasync uses the `WebsocketAuthProtocol` from [ws_auth](https://github.com/newvicx/ws_auth) to open and receive data from a websocket connection. The `WebsocketClient` wraps and manages a protocol instance and exposes a method to receive messages from the connection. There are some more advanced features such as reconnects, updates, and watchdogs; these are covered in the [Advanced Usage](https://github.com/newvicx/piwebasync/blob/main/docs/Advanced%20Usage.md) section.

To open a websocket connection, you must `await` a `WebsocketClient` instance or use the `async with` syntax. This will be familiar to those who have used the [Websockets](https://websockets.readthedocs.io/en/stable/reference/client.html) client library in the past. In fact, the majority of the parameters in the `WebsocketClient` are identical to the [Websockets Connect API](https://github.com/aaugustin/websockets/blob/main/src/websockets/legacy/client.py)

### Authentication

The Websockets API does not natively support customized authentication how HTTPX does. To circumvent this, piwebasync uses the `WebsocketAuthProtocol` from ws_auth which is a custom protocol built to support HTTPX style auth flows. Visit the [ws_auth repository](https://github.com/newvicx/ws_auth) to see how to implement custom authentication in the `WebsocketClient`

### Messages

If a message is received on the connection, a call to `recv` will return a `WebsocketMessage` instance which has 1 default property...

> **url** (*str*): request URL that produced response

A `WebsocketMessage` instances has the same behavior and methods as an `HTTPResponse` instance. See the "Responses" section above for more information.

### Iteration 

A `WebsocketClient` instance can be used as async iterator to continuously receive messages from the channel as they come in...

```python
async with piwebasync.WebsocketClient(request) as client:
	async for message in client:
		print("Got a message")
```

### Detecting the End of a Stream

When the connection is closed, `recv` raises `~piwebasync.exceptions.ChannelClosed`. Specifically, it raises `~piwebasync.exceptions.ChannelClosedOK` after a normal connection closure and `~piwebasync.exceptions.ChannelClosedError` after a protocol error or a network failure. This is how you detect the end of the message stream. You can catch this error in receiver task or within the context manager and handle it appropriately...

```python
async with piwebasync.WebsocketClient(request) as client:
    try:
		async for message in client:
			print("Got a message")
    except ChannelClosedError as err:
        print(f"Channel closed due to some error {repr(err.__cause__)}")
        raise
```

## Authentication 

### Kerberos

There are two existing libraries I encourage you to look at if your PI Web API server is secured through Kerberos...

- [async_negotiate_sspi](https://github.com/newvicx/async_negotiate_sspi): has both an HTTP and Websocket auth flow for single-sign-on on Windows systems through SSPI
- [httpx_gssapi](https://github.com/pythongssapi/httpx-gssapi): will only work for HTTP requests but it can be easily ported to work for websockets. Relies on GSSAPI

### Bearer

I did not find any HTTPX style auth flows for bearer authentication but I'm sure the community could correct me on that or develop one
