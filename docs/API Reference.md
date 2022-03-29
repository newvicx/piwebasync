# API Reference
## Clients

### HTTPClient

*class* ***piwebasync.HTTPClient***(*, *auth=None*, *headers=None*, *cookies=None*, *verify=True*, *safe_chars=None*, *cert=None*, *proxies=None*, *mounts=None*, *timeout=None*, *follow_redirects=False*, *limits=DEFAULT_LIMITS*, *max_redirects=DEFAULT_MAX_REDIRECTS*, *event_hooks=None*, *transport=None*, *trust_env=True*)

Asynchronous HTTP client for making requests to a Pi Web API server

**Usage**

```python
request = Controller(scheme, host, root=root).streams.get_end(webid)
async with piwebasync.HTTPClient() as client:
    response = await client.get(request)
```

**Parameters**

> **auth** (*Optional*): An authentication class to use when sending requests.
> 
> **headers** (*Optional*): Dictionary of HTTP headers to include when sending requests.
> 
> **cookies** (*Optional*): Dictionary of Cookie items to include when sending requests.
> 
> **verify** (*Optional*): SSL certificates (a.k.a CA bundle) used to verify the identity of requested hosts. Either True (default CA bundle), a path to an SSL certificate file, an ssl.SSLContext, or False (which will disable verification).
> 
> **safe_chars** (*Optional*): String of safe characters that should not be percent encoded
> 
> **cert** (*Optional*): An SSL certificate used by the requested host to authenticate the client. Either a path to an SSL certificate file, or two-tuple of (certificate file, key file), or a three-tuple of (certificate file, key file, password).
> 
> **proxies** (*Optional*): A dictionary mapping proxy keys to proxy URLs.
> 
> **mounts** (*Optional*): A dictionary of mounted transports against a given schema or domain
> 
> **timeout** (*Optional*): The timeout configuration to use when sending requests.
> 
> **follow_redirects** (*Optional*): Boolean flag indicating if client should follow redirects
> 
> **limits** (*Optional*): The limits configuration to use.
> 
> **max_redirects** (*Optional*): The maximum number of redirect responses that should be followed.
> 
> **event_hooks** (*Optional*): Dictionary of async callables with signature *Callable[[Union[httpx.Request, httpx.Response]], Union[httpx.Request, httpx.Response]]*
> 
> **transport** (*Optional*): A transport class to use for sending requests over the network.
> 
> **trust_env** (*Optional*) Enables or disables usage of environment variables for configuration.

*coroutine* ***HTTPClient.request***(*request*, *, *headers=None*, *json=None*, *auth=USE_CLIENT_DEFAULT*, *follow_redirects=USE_CLIENT_DEFAULT*, *timeout=USE_CLIENT_DEFAULT*, *extensions=None*)

Verify and send APIRequest

**Parameters**

> **request** (*APIRequest*): request to send
> 
> **headers** (*Optional*): Dictionary of HTTP headers to include for this request
> 
> **json** (*Optional*): Dictionary of JSON encoded data to send in request body
> 
> **auth** (*Optional*): An authentication class to use for this request
> 
> **follow_redirects** (*Optional*): Boolean flag indicating client should follow redirects for this request
> 
> **timeout** (*Optional*): The timeout configuration to use for this request
> 
> **extensions** (*Optional*): Dictionary of request extensions to use for this request

**Returns**

> **HTTPResponse**: response object containing response info and content

**Raises**

> **ValueError**: invalid APIRequest protocol for client or invalid HTTP method for controller
> 
> **TypeError**: request is not an instance of APIRequest
> 
> **HTTPClientError**: error sending request. Always originates from an error in the underlying client object. Will always have a `__cause__` attribute

*coroutine* ***HTTPClient.get***(*request*, *, *headers=None*, *auth=USE_CLIENT_DEFAULT*, *follow_redirects=USE_CLIENT_DEFAULT*, *timeout=USE_CLIENT_DEFAULT*, *extensions=None*)

Verify and send a GET APIRequest

**Parameters**

> See ***HTTPClient.request*** (Does not accept *json* parameter)

**Returns**

> See ***HTTPClient.request***

**Raises**

> See ***HTTPClient.request***

*coroutine* ***HTTPClient.post***(*request*, *, *headers=None*, *json=None*, *auth=USE_CLIENT_DEFAULT*, *follow_redirects=USE_CLIENT_DEFAULT*, *timeout=USE_CLIENT_DEFAULT*, *extensions=None*)

Verify and send a POST APIRequest

**Parameters**

> See ***HTTPClient.request***

**Returns**

> See ***HTTPClient.request***

**Raises**

> See ***HTTPClient.request***

*coroutine* ***HTTPClient.put***(*request*, *, *headers=None*, *json=None*, *auth=USE_CLIENT_DEFAULT*, *follow_redirects=USE_CLIENT_DEFAULT*, *timeout=USE_CLIENT_DEFAULT*, *extensions=None*)

Verify and send a PUT APIRequest

**Parameters**

> See ***HTTPClient.request***

**Returns**

> See ***HTTPClient.request***

**Raises**

> See ***HTTPClient.request***

*coroutine* ***HTTPClient.patch***(*request*, *, *headers=None*, *json=None*, *auth=USE_CLIENT_DEFAULT*, *follow_redirects=USE_CLIENT_DEFAULT*, *timeout=USE_CLIENT_DEFAULT*, *extensions=None*)

Verify and send a PATCH APIRequest

**Parameters**

> See ***HTTPClient.request***

**Returns**

> See ***HTTPClient.request***

**Raises**

> See ***HTTPClient.request***

*coroutine* ***HTTPClient.delete***(*request*, *, *headers=None*, *json=None*, *auth=USE_CLIENT_DEFAULT*, *follow_redirects=USE_CLIENT_DEFAULT*, *timeout=USE_CLIENT_DEFAULT*, *extensions=None*)

Verify and send a DELETE APIRequest

**Parameters**

> See ***HTTPClient.request***

**Returns**

> See ***HTTPClient.request***

**Raises**

> See ***HTTPClient.request***

*coroutine* ***HTTPClient.close***()

Close the underlying client

### WebsocketClient

*class* ***piwebasync.WebsocketClient***(*request*, *, *create_protocol=None*, *auth=None*, *compression="deflate"*, *origin=None*, *extensions=None*, *subprotocols=None*, *extra_headers=None*, *open_timeout=10*, *reconnect=False*, *dead_channel_timeout=3600*, *ping_interval=20*, *ping_timeout=20*, *close_timeout=3*, *max_size=2**20*, *max_queue=2**5*, *read_limit=2**16*, *write_limit=2**16*, *loop=None*)

Asynchronous Websocket client to PI Web API channel endpoint

**Usage**

```python
# As async context manager
async with WebsocketClient(request) as channel:
    message = await channel.recv()

# No context manager
channel = await WebsocketClient(request)
try:
    message = await channel.recv()
finally:
    await channel.close()
    
# Async iterator
async with WebsocketClient(request) as channel:
    async for message in channel:
        print("Got a message!")
```

**Parameters**

> **request** (*APIRequest*): PI Web API channel endpoint to connect to
> 
> **create_protocol** (*Optional*) – factory for the asyncio.Protocol managing the connection; defaults to WebsocketAuthProtocol; may be set to a wrapper or a subclass to customize connection handling.
> 
> **auth** (*Optional*): An authentication class to use during opening handshake
> 
> **compression** (*Optional*) – shortcut that enables the “permessage-deflate” extension by default; may be set to None to disable compression; see the compression guide for details.
> 
> **origin** (*Optional*) – value of the Origin header. This is useful when connecting to a server that validates the Origin header to defend against Cross-Site WebSocket Hijacking attacks.
> 
> **extensions** (*Optional*) – list of supported extensions, in order in which they should be tried.
> 
> **subprotocols** (*Optional*) – list of supported subprotocols, in order of decreasing preference.
> 
> **extra_headers** (*Optional*) – arbitrary HTTP headers to add to the request.
> 
> **open_timeout** (*Optional*) – timeout for opening the connection in seconds; None to disable the timeout
> 
> **reconnect** (*Optional*): if `True`, client will attempt to reconnect on network or protocol failure
> 
> **dead_channel_timeout** (*Optional*): if `reconnect=True`, client will try to reestablish connection for at most dead_channel_timeout seconds. Set to None to disable timeout
> 
> **ping_interval** (*Optional*) – delay between keepalive pings in seconds; None to disable keepalive pings.
> 
> **ping_timeout** (*Optional*) – timeout for keepalive pings in seconds; None to disable timeouts.
> 
> **close_timeout** (*Optional*) – timeout for closing the connection in seconds; for legacy reasons, the actual timeout is 4 or 5 times larger.
> 
> **max_size** (*Optional*) – maximum size of incoming messages in bytes; None to disable the limit.
> 
> **max_queue** (*Optional*) – maximum number of incoming messages in receive buffer; None to disable the limit.
> 
> **read_limit** (*Optional*) – high-water mark of read buffer in bytes.
> 
> **write_limit** (*Optional*) – high-water mark of write buffer in bytes.

**Attributes**

> *WebsocketClient*.***is_closed***: `True` when channel is closed; `False` otherwise
> 
> *WebsocketClient*.***is_closing***: `True` when channel is closing; `False` otherwise
> 
> *WebsocketClient*.***is_open***: `True` when channel is open; `False` otherwise
> 
> *WebsocketClient*.***is_reconnecting***: `True` when channel is reconnecting; `False` otherwise

*A channel is considered OPEN when there is an active connection and the client can receive data. When RECONNECTING, the client cannot receive new messages. A user can fetch messages from the client in any state so long as there are messages buffered*

*coroutine* ***WebsocketClient.recv***()

Receive the next message from the buffer.

When the connection is closed, `recv` raises `~piwebasync.exceptions.ChannelClosed`. Specifically, it raises `~piwebasync.exceptions.ChannelClosedOK` after a normal connection closure and `~piwebasync.exceptions.ChannelClosedError` after a protocol error or a network failure. This is how you detect the end of the message stream.

Canceling `recv` is safe. There's no risk of losing the next message. The next invocation of `recv` will return it.

**Returns**

> **WebsocketMessage**

**Raises**

> **ChannelClosed**: when the connection is closed
> 
> **RuntimeError**: if two coroutines call `recv` concurrently

*coroutine* ***WebsocketClient.update***(*request*, *rollback=True*)

Update Channel endpoint

This method does not interrupt `recv`. Any messages already in the client buffer will remain there. New messages will reflect the updated endpoint accordingly. If `update` fails with a *ChannelUpdateError*, the channel will remain in a CLOSED state

**Parameters**

> **request** (*APIRequest*): The new endpoint to connect to
>
> **rollback** (*bool*): The channel will attempt to rollback to the previous endpoint

**Raises**

> **ChannelRollback**: Unable to establish connection to new endpoint but rollback to previous endpoint was successful
> 
> **ChannelUpdateError**: Unable to establish connection to new endpoint
> 
> **ChannelClosed**: The channel is closed
> 
> **ValueError**: Request is invalid
> 
> **RuntimeError**: if two coroutines call `update` concurrently

*coroutine* ***WebsocketClient.close***()

Close the client

Execute closing sequence. Calls to `recv` after the closing sequence has started will raise *ChannelClosed*

## Models

### APIRequest (pydantic.BaseModel)

*class*  ***piwebasync.APIRequest***(*root*, *method*, *protocol*, *controller*, *scheme*, *host*, *, *port=None*, *action=None*, *webid=None*, *add_path=None*, ***kwargs*)

Base model for Pi Web API requests. An API request is passed to a client instance to handle the request. You will not typically create APIRequest objects yourself. Generally, you should use the *Controller* object instead. However, for non supported controllers and controller methods you may want to create your own APIRequest directly

**Parameters**
>  **root** (*str*): root path to PI Web API
>  
>  **method** (*str*): the HTTP method for the request
>  
>  **protocol** (*str*): request protocol to use; either *"HTTP"* or *"Websockets"*
>  
>  **controller** (*str*): the controller being accessed on the PI Web API
>  
>  **scheme** (*str*): URL scheme; *"http"*, *"https"*, *"ws"*, *"wss"*
>  
>  **host** (*str*): PI Web API host address
>  
>  **port** (*Optional(str)*): the port to connect to
>  
>  **action** (*Optional(str)*): the PI Web API controller method, this is a path parameter
>  
>  **webid** (*Optional(str)*): the WebId of a resource, this is a path parameter
>  
>  **add_path** (*Optional(list[str])*): additional path parameters to be included. List elements are added to the end of the path in order separated by a "/"
>  
>  **kwargs** (*Optional(Any)*): query parameters for controller method
>  

**Attributes**

>  *APIRequest*.***absolute_url***: Returns full URL path as str
>  
>  *APIRequest*.***params***: Returns normalized query params as dict
>  
>  *APIRequest*.***path***: Returns URL path
>  
>  *APIRequest*.***query***: Returns normalized query params as str
>  
>  *APIRequest*.***raw_path***: Returns URL target as str

### APIResponse (pydantic.BaseModel)

*class* ***piwebasync.APIResponse***(***kwargs*)

Base model for PI Web API responses. Users will never create APIResponse objects directly. Instead, *HTTPResponse* and *WebsocketMessage* instances will be returned from the *HTTPClient* and *WebsocketClient* respectively. The APIResponse model handles errors in the body of a response and normalizes all arguments from camel case to snake case

**Parameters**

> **kwargs** (*Optional(Any)*): Any content to be included in response

**Properties**

> *APIResponse*.***raw_response***: Reproduce raw response body from PI Web API as bytes 

*method* **APIResponse.select**(**fields*)

Returns the values of the selected fields from the response content. 'fields' are defined using dot notation (Top.Nested.NestedNested)

**Usage**

Example response body...

```json
{
"Items": [
	{
	"Timestamp": "2014-07-22T14:00:00Z",
	"UnitsAbbreviation": "m",
	"Good": true,
	"Questionable": false,
	"Substituted": false,
	"Annotated": false,
	"Value": {
		"Name": "Off",
		"Value": 0,
	}
	},
	{
	"Timestamp": "2014-07-22T14:00:00Z",
	"UnitsAbbreviation": "m",
	"Good": true,
	"Questionable": false,
	"Substituted": false,
	"Annotated": false,
	"Value": {
		"Name": "Off",
		"Value": 0,
	}
	}
],
"Links": {}
}
```

```python
selection = response.select("Items.Timestamp", "Items.Good", "Items.Value.Value", "Items.Value.Name")
```

Output...

```
>>> selection
{
    "Items.Timestamp": ["2014-07-22T14:00:00Z", "2014-07-22T14:00:00Z"],
    "Items.Good": [True, True],
    "Items.Value.Value": [0, 0]
    "Items.Value.Name": ["Off", "Off"]
}
```

Identical field keys across different lists in the JSON response will be aggregated into a list of lists for example...

```json
{
  "Items": [
    {
      "WebId": "I1AbEDqD5loBNH0erqeqJodtALAYIKyyz2F5BGAxQAVXYRDBAGyPedZG1sUmxOOclp3Flwg",
      "Name": "Water",
      "Path": "\\\\MyAssetServer\\MyDatabase\\MyElement|Water",
      "Items": [
        {
          "Timestamp": "2014-07-22T14:00:00Z",
          "UnitsAbbreviation": "m",
          "Good": true,
          "Questionable": false,
          "Substituted": false,
          "Annotated": false,
          "Value": 12.3
        },
        {
          "Timestamp": "2014-07-22T14:00:00Z",
          "UnitsAbbreviation": "m",
          "Good": true,
          "Questionable": false,
          "Substituted": false,
          "Annotated": false,
          "Value": 12.3
        }
      ],
      "UnitsAbbreviation": "m",
      "Links": {
        "Self": "https://localhost.osisoft.int/piwebapi/attributes/I1AbEDqD5loBNH0erqeqJodtALAYIKyyz2F5BGAxQAVXYRDBAGyPedZG1sUmxOOclp3Flwg"
      }
    },
    {
      "WebId": "I1AbEDqD5loBNH0erqeqJodtALAYIKyyz2F5BGAxQAVXYRDBAGyPedZG1sUmxOOclp3GSWd",
      "Name": "Fire",
      "Path": "\\\\MyAssetServer\\MyDatabase\\MyElement|Fire",
      "Items": [
        {
          "Timestamp": "2014-07-22T14:00:00Z",
          "UnitsAbbreviation": "m",
          "Good": true,
          "Questionable": false,
          "Substituted": false,
          "Annotated": false,
          "Value": 451
        },
        {
          "Timestamp": "2014-07-22T14:00:00Z",
          "UnitsAbbreviation": "m",
          "Good": true,
          "Questionable": false,
          "Substituted": false,
          "Annotated": false,
          "Value": 451
        }
      ],
      "UnitsAbbreviation": "m",
      "Links": {
        "Self": "https://localhost.osisoft.int/piwebapi/attributes/I1AbEDqD5loBNH0erqeqJodtALAYIKyyz2F5BGAxQAVXYRDBAGyPedZG1sUmxOOclp3Flwg"
      }
    }
  ],
  "Links": {}
}
```

```python
selection = response.select("Items.Name", "Items.Items.Value")
```

Output...

```
>>> selection
{
    "Items.Name": ["Water", "Fire"],
    "Items.Items.Value": [[12.3, 12.3], [451, 451]]
}
```

Keys not found will return an empty list. For example, using the response content from above...

```python
selection = response.select("Items.Name", "Items.Items.Value", "Items.EngineeringUnits")
```

Output...

```
>>> selection
{
    "Items.Name": ["Water", "Fire"],
    "Items.Items.Value": [[12.3, 12.3], [451, 451]]
    "Items.EngineeringUnits": []
}
```

Search will always stop and return value at bottom level even if there is another field specified by the user in select. This behavior is nice for a non uniform response structure. For example...

```json
{
"Items": [
	{
	"Timestamp": "2014-07-22T14:00:00Z",
	"UnitsAbbreviation": "m",
	"Good": true,
	"Questionable": false,
	"Substituted": false,
	"Annotated": false,
	"Value": 0,
	},
	{
	"Timestamp": "2014-07-22T14:00:00Z",
	"UnitsAbbreviation": "m",
	"Good": true,
	"Questionable": false,
	"Substituted": false,
	"Annotated": false,
	"Value": {
		"Name": "Interface Bad Value",
		"Value": -1,
	}
	}
],
"Links": {}
}
```

We can get "Value" from both elements in items with the follow select statement...

```python
selection = response.select("Items.Value.Value")
```

Output...

```
>>> selection
{
    "Items.Value.Value": [0, -1]
}
```

**Parameters**

> **fields** (*Optional(str)*): selected fields to extract and normalize from response content

**Returns**

> **selection** (*dict[str, list]*): Normalized dictionary of selected fields

#### HTTPResponse (APIResponse)

*class* ***piwebasync.HTTPResponse***(*status_code*, *url*, *headers*, ***kwargs*)

**Parameters**

> **status_code** (*int*): status code returned from server
> 
> **url** (*str*): request URL that produced response
> 
> **headers** (*httpx.Headers*): response headers from server
> 
> **kwargs** (dict[str, Any]): response content

*method* **HTTPResponse.raise_for_status**()

Non 200 status codes will raise an `HTTPStatusError`. Additionally, if a successful response could not be processed due to a `JSONDecodeError`, this will also raise an `HTTPStatusError`

#### WebsocketMessage (APIResponse)

*class* ***piwebasync.WebsocketMessage***(*url*, ***kwargs*)

**Parameters**

> **url** (*str*): request URL that produced response
> 
> **kwargs** (dict[str, Any]): response content

### Controller

*class* ***piwebasync.Controller***(*scheme*, *host*, *, *port=None*, *root="/"*)

Base class for all PI Web API controllers. Provides a standardized API for constructing APIRequests. All supported PI Web API controllers can be accessed as attributes of the base Controller instance

**Usage**

```python
# Chaining
request: APIRequest = Controller(scheme, host, port, root).streams.get_end(webid)

# Reuse base URL
controller: Controller = Controller(scheme, host, port, root)
request_1: APIRequest = controller.streams.get_end(webid)
request_2: APIRequest = controller.streams.get_recorded(webid)
```

**Parameters**

> **scheme** (*str*): URL scheme; *"http"*, *"https"*, *"ws"*, *"wss"*
> 
> **host** (*str*): PI Web API host address
> 
> **port** (*Optional(str)*): the port to connect to
> 
> **root** (*Optional(str)*): root path to PI Web API

**Attributes**

> *Controller*.***assetdatabases***: PI Web API AssetDatabases controller
> 
> *Controller*.***assetservers***: PI Web API AssetServers controller
> 
> *Controller*.***attributes***: PI Web API Attributes controller
> 
> *Controller*.***dataservers***: PI Web API DataServers controller
> 
> *Controller*.***elements***: PI Web API Elements controller
> 
> *Controller*.***eventframes***: PI Web API EventFrames controller
> 
> *Controller*.***points***: PI Web API Points controller
> 
> *Controller*.***streams***: PI Web API Streams controller
> 
> *Controller*.***streamsets***: PI Web API StreamSets controller

You can view the supported controller methods by examining the [source code](https://github.com/newvicx/piwebasync/tree/main/piwebasync/api/controllers)

## Exceptions

piwebasync defines the following exception hierarchy:

- `PIWebAsyncException`
  - `APIException`
    - `SerializationError`
  - `HTTPClientError`
    - `HTTPStatusError`
  - `WebsocketClientError`
    - `ChannelClosed`
      - `ChannelClosedError`
      - `ChannelClosedOK`
    - `ChannelUpdateError`
    - `ChannelRollback`
    - `WatchdogTimeout`

### PIWebAsyncException (Exception)

Base exception for all piwebasync exceptions

### SerializationError(APIException)

Raised when a controller method argument cannot be serialized to URL safe string

### HTTPClientError (PIWebAsyncException)

Raised when an error occurs in the the underlying client object of the HTTPClient. Always has a `__cause__`

### HTTPStatusError (PIWebAsyncException)

Raised when a non 200 status code is received in an HTTP request or a `JSONDecodeError` occurred parsing the response

### WebsocketClientError (PIWebAsyncException)

Base exception for all exceptions in WebsocketClient

### ChannelClosed (WebsocketClientError)

Raised when `recv` or `update` is called when client is closed

### ChannelClosedError (ChannelClosed)

Raised when an error occurs during client operation that causes the client to close. Always has a `__cause__`

### ChannelClosedOK (ChannelClosed)

Raised when client closed via normal closing sequence. Does not have a `__cause__`

### ChannelUpdateError (WebsocketClientError)

Raised when the client attempts to open connection via `update` method and the method times out

### ChannelRollback (WebsocketClientError)

Raised when the client rolls back to the previous endpoint after a failed update

### WatchdogTimeout (WebsocketClientError)

Raised when the client is unable to reconnect to the remote host in `dead_channel_timeout` seconds
