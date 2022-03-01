# Quick Start

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

The HTTPClient supports all HTTP methods that the PI Web API does including; GET, POST, PUT, PATCH, and DELETE. Also it is nearly identical to the httpx.AsyncClient API

*Note: Not all controllers nor all controller methods have been implemented in piwebasync (yet!). While the HTTPClient does support all the aforementioned HTTP methods you may need to construct the URL yourself rather than using the Controller class as shown above*

For opening a websocket connection, use the WebsocketClient...
```python
	request = piwebasync.Controller(scheme="wss",host="myhost.com", root="piwebapi").streams.get_channel("point_webid")

	async with piwebasync.WebsocketClient(request) as client:
		async for message in client:
			print("Got a message")
```

The WebsocketClient API is nearly identical to the websockets.legacy.Connection API with a few features added and few features stripped out. See the Adavanced Usage section for more info on the WebsocketClient

## Constructing Requests

The Controller class is the base class for constructing all API requests. It provides a structured and validated API for deriving endpoint URL's. A PI Web API request URL has the following structure

	{scheme}://{host}:{port}/{root}/{controller}/{webid}/{action}/{additional path params}?{query params}

When creating a Controller instance you must provide at least a scheme and host, supported schemes are http, https, ws, wss

### Basic

All supported PI Web API controllers can be directly accessed as properties of the Controller class, and all supported actions are functions of that controller. For example, the Streams controller has the GetEnd method. Constructing that request in piwebasync would look something like this...

	request = Controller(scheme="https",host="myhost.com", root="piwebapi").streams.get_end("point_webid")

This returns an APIRequest which can be passed directly into an HTTPClient instance. The above is equivalent to the URL...

	https://myhost.com/piwebapi/streams/point_webid/end

The advantage to using a Controller instance is that all supported methods are validated and type hinted. You can pass native python types in native python syntax and the URL construction will be handled automatically. Lets take a more complex example...

### Formatting and Validation

The StreamSet controller has an analogous GetEndAdHoc method which allows you to query for multiple PI points in a single request. You can request multiple WebId's by specifying the WebId parameter multiple times. For example...

	https://myhost.com/piwebapi/streamsets/end?webId=point_1_webid&webId=point_2_webid

Lets add in some selected fields...

	https://myhost.com/piwebapi/streamsets/end?webId=point_1_webid&webId=point_2_webid&selectedFields=Items.WebId;Items.Items.Timestamp;Items.Items.Value

With 100 points along with other query parameters, constructing these URL's can become laborious and error prone. Instead, lets look at how we can construct this endpoint in piwebasync
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

piwebasync will handle all the query parameter formatting including, converting parameters to lower camel case format, adding a semi colon between each selected field, and specifying "webId" for each webid in the list. You can view the formatted URL by accessing the `absolute_url` property on the APIRequest
```python
	print(request.absolute_url)
```

You should get the following output

	https://myhost.com/piwebapi/streamsets/end?webId=point_1_webid&webId=point_2_webid&selectedFields=Items.WebId;Items.Items.Timestamp;Items.Items.Value

Lastly, all controller methods such as the `.get_end()` method will not accept any parameters not supported by the PI Web API so you can be sure that any URL  will have valid query parameters.

## Making Requests

Almost all methods in PI Web API happen over HTTP with the lone exception being the GetChannel method for both the Streams and StreamSets controllers which use the Websocket protocol. piwebasync provides an HTTPClient for handling HTTP requests concurrently.

The preferred way of using the HTTPClient is as an async context manager...
```python
	async with HTTPClient() as client:
		response = await client.request(request)
```

### Responses

Requests return an instance of HTTPResponse which has 3 default properties...

- status_code (int): the HTTP status code returned from the server
- headers (httpx.Headers): the response headers returned from the server
- url (str): the absolute URL for the request that was made

Additionally you can access the content of the response body by calling the `.dict()` method. This will return the JSON response as a dictionary. Alternatively, the top level parameters of the response are also attributes of the response so you can access them via dot notation. For example, consider the example response content...
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

All the parameters of the in above response are in the top level of the response body except for "Self" which is nested in "Links". So for example you can access "EngineeringUnits" directly from the HTTPResponse object using snake case...

	response.engineering_units

For JSON normalization of responses see the Advanced Usage section

### Config and Authentication

Under the hood, piwebasync uses the ExClient from httpx_extensions to facilitate the HTTP requests. This client provides easy support for Kerberos and NTLM authentication but it also supports all existing HTTPX auth flows including Bearer authentication. The HTTPClient is really just a simple wrapper around the ExClient and just about every parameter in the HTTPClient constructor is passed directly into the ExClient constructor

### SafeChars

Oftentimes, characters in requests are not URL safe such as "\\", "%", etc. These characters are usually percent encoded to their URL safe equivalents. The PI Web API says that all appropriate characters should be percent encoded, but in practice, I have found some situations where percent encoding has led to error responses. For these situations you can specify `safe_chars` as a string of characters which will not be encoded and instead sent as is.

For example, take the following URL...

	https://pivision.com/piwebapi/points/?path=\\MyPIServer\PointName

HTTPX and by extension, the ExClient would encode and send this URL as...

	https://pivision.com/piwebapi/points/?path=%2F%2FMyPIServer%2FPointName

This will lead to an error in the PI Web API (Tested on PI Web API 2019 SP1)
```json
{
	"Errors": [
		"The specified path was not found. If more details are needed, please contact your PI Web API administrator for help in enabling debug mode."
	]
}
```

To fix this you can specify the `safe_chars` in the HTTPClient constructor...
```python
	client = HTTPClient(safe_chars='/:?=\\')
```

*Note: You need to include all characters that have a percent encoding when specifying safe_chars even if these characters would not have been percent encoded previously*

