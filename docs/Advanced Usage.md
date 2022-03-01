# Advanced Usage

## Websockets

The `WebsocketClient` was built with data streaming services in mind. Lets explore some of the more advanced features by building a pseudo code outline for a simple streaming service.

### Application Overview

We want to build a service that...

1. Opens a websocket connection to a channel endpoint
2. Continuously receives data from the channel, extracts the required information, and passes the message to a message broker

The service should...

1. Be robust (i.e. resistant to network hiccups)
2. Notify an admin of major problems (such as a long network outage)
3. Be able to update the query without requiring the service to shutdown

Lets start with a simple service that accomplishes the minimum requirements (remember the message broker side of this is pseudo code)...

```python
import asyncio
from async_negotiate_sspi import NegotiateAuthWS
from piwebasync import Controller, WebsocketClient
from broker_service import broker_connection

async def publish_task(queue: asyncio.Queue):
    publisher = broker_connection(connect_url, role="publisher")
    try:
        while True:
            message = await queue.get()
            queue.task_done()
            await publisher.publish(message)
    except asyncio.CancelledError:
        await publisher.close()
        raise
        
async def receive_new_data_task(channel: WebsocketClient, queue: asyncio.Queue):
    async for message in channel:
        publish_message = message.select("Items.Name", "Items.Items.Timestamp", "Items.Items.Value")
        await queue.put(publish_message)
        
async def main():
    loop = asyncio.get_event_loop()
    request = Controller(scheme, host, root=root).streams.get_channel(webid)
    queue = asyncio.Queue()
	async with WebsocketClient(request, auth=NegotiateAuthWS()) as channel:
        receive_task = loop.create_task(receive_new_data_task(channel, queue))
        publish_task = loop.create_task(publish_task(queue))
        try:
            await asyncio.wait(
                [receive_task, publish_task],
                return_when=asyncio.FIRST_COMPLETED
            )
       	except asyncio.CancelledError:
            if not publish_task.done():
                publish_task.cancel()
            if not receive_task.done():
                receive_task.cancel()
        await asyncio.gather(receive_task, publish_task)

if __name__ == "__main__":
	asyncio.run(main())
```

So this covers our first two requirements...

> - Opens a websocket connection to a channel endpoint
> - Continuously receives data from the channel, extracts the required information and passes the message to a message broker

There are some problems though. What happens if we experience a network interruption or protocol error? Well first, `receive_task` will continue to get messages from the channel so long as messages are buffered. But, once the buffer is exhausted, it will raise a `ChannelClosedError` as a result network error and the service will crash. Our requirements say the service should...

> - Be robust (i.e. resistant to network hiccups)

What we want is for the channel to try and reconnect if the channel closes unexpectedly. The `WebsocketClient` has a way to handle this transparently.

### Reconnects

You can specify `reconnect=True` in the `WebsocketClient` constructor and if there is a network interruption or protocol error; rather than raising an error once the buffer is exhausted, the client will attempt to reopen the channel in the background. We can modify our code to support reconnects with a single line change...
```python
async with WebsocketClient(request, auth=NegotiateAuthWS(), reconnect=True) as channel:
```

Now, if a network interruption occurs, `receive_task` wont raise an error. Instead it, will wait until the channel re-opens and then continue receiving messages as if the interruption never occurred.

Alright so this thing is now reasonably robust but (there's always a but...), if we are running a data streaming service and the PI server experiences a long outage we don't want to be trying to reconnect for hours on end. Remember the fourth requirement...

> - Notify an admin of major problems (such as a long network outage)

We probably want an error to be raised after a certain amount of time so we can catch it and notify someone that the service isn't working right now. The `WebsocketClient` has a built in watchdog for this purpose.

### Watchdog (dead_channel_timeout)

You can specify a `dead_channel_timeout` (in seconds) in the `WebsocketClient` constructor. If `reconnect=True` a watchdog task will run automatically in the background and monitor when the channel disconnects. It will wait `dead_channel_timeout` seconds for the connection to be re-opened and if the channel doesn't re-open, the watchdog will close the channel and raise a `WatchdogTimeout` exception. Lets specify a reasonable timeout for our service to try and reconnect. Again we can do this with a single line change...

```python
async with WebsocketClient(request, auth=NegotiateAuthWS(), reconnect=True, dead_channel_timeout=1800) as channel:
```

Now, if the client is unable to reconnect for 1800 seconds (30 minutes) the channel will be closed and `receive_task` will raise a `ChannelClosedError` again. Lets see how we can use that by modifying `receive_new_data_task`.

```python
async def receive_new_data_task(channel: WebsocketClient, queue: asyncio.Queue):
    try:
        async for message in channel:
            publish_message = message.select("Items.Name", "Items.Items.Timestamp", "Items.Items.Value")
            await queue.put(publish_message)
    except ChannelClosedError as err:
        if isinstance(err.__cause__, WatchdogTimeout):
            raise WatchdogTimeout
        raise
```

We can detect the end of stream by catching `ChannelClosedError` which will always have a `__cause__` associated with it. If the exception was caused by a `WatchdogTimeout` we want to raise that so that our `main` function can do something with it. So lets modify `main` now...

```python
async def main():
    loop = asyncio.get_event_loop()
    request = Controller(scheme, host, root=root).streams.get_channel(webid)
    queue = asyncio.Queue()
	async with WebsocketClient(request, auth=NegotiateAuthWS()) as channel:
        receive_task = loop.create_task(receive_new_data_task(channel, queue))
        publish_task = loop.create_task(publish_task(queue))
        try:
            await asyncio.wait(
                [receive_task, publish_task],
                return_when=asyncio.FIRST_COMPLETED
            )
       	except asyncio.CancelledError:
            if not publish_task.done():
                publish_task.cancel()
            if not receive_task.done():
                receive_task.cancel()
        try:
        	await asyncio.gather(receive_task, publish_task)
        except WatchdogTimeout:
            await notification_service.notify()
            raise
```

Now if the service shuts down because it was unable to reconnect you can be notified about it.

Alright, so four requirements down, one to go. The service should...

> - Be able to update the query without requiring the service to shutdown

As you might have guessed, the `WebsocketClient` has method for handling this as well.

### Updating the Client Endpoint

Consider this scenario, your service is running great and you're streaming all the data you need. All of sudden you have a new PI tag or AF element that you want to stream data for. There are some naïve options...

1. You can open a new websocket connection that streams just that point or element
2. You can update the config file where you specified all the points/elements and restart the streaming service picking up the new config

Besides the fact that neither solution meets our requirement there are some other issues...

- With option 1 you are not efficiently using your connection by dedicating one connection to a single point
- With option 2 we are interrupting the service and if the buffer has unconsumed messages those message will be lost

A better approach would be to modify the existing endpoint and re-open the connection with the modified endpoint. Ideally this should allow us to continue to consume existing messages from the buffer and any new messages will reflect the new query. For this, we would use the `.update()` method.

Lets add a little more pseudo code to show a broker consumer process listening for an update to the channel...
```python
import asyncio
from piwebasync import APIRequest, Controller, WebsocketClient
from piwebasync.exceptions import ChannelClosedError, ChannelUpdateError, WatchdogTimeout

async def receive_task(channel: WebsocketClient):
	async for message in channel:
		print("Got a message")
		
async def update_listener_task(channel: WebsocketClient):
	listener = await messaging_service.connect("connect_url")
	async for update_details in listener:
		# We decided to update the channel by sending a message through the messaging service
		request = APIRequest(**update_details)
		await channel.update(request)

async def main():
	loop = asyncio.get_event_loop()
	request = Controller(scheme, host, root=root).streams.get_channel(webid)
	try:
		async with WebsocketClient(request, reconnect=True) as channel:
			receive_task = loop.create_task(receive_task(channel))
			listener_task = loop.create_task(listener_task(channel))
			await asyncio.wait([receive_task, listener_task], return_when=asyncio.FIRST_COMPLETED)
			if receive_task.done() and not listener_task.done():
				try:
					await receive_task
				except ChannelClosedError:
					if isinstance(err.__cause__, WatchdogTimeout):
						# notify admin
						listener_task.cancel()
						raise
			await asyncio.gather(receive_task, listener_task)
	except (ChannelClosedError, ChannelUpdateError) as err:
		raise

if __name__ == "__main__":
	asyncio.run(main())
```

*Note: This contains pseudo code with improper error handling. It is simply a demonstration of the concept*

## Authentication
### HTTP
For HTTP requests, you can plug in any authentication handler that inherits from [httpx.Auth](https://github.com/encode/httpx/blob/master/httpx/_auth.py). See the [HTTPX documentation](https://www.python-httpx.org/advanced/#customizing-authentication) on customizing authentication.
### Websockets
For Websocket connections, similar to HTTP requests, you can plug in any authentication handler that inherits from [ws_auth.Auth](https://github.com/newvicx/ws_auth/blob/main/ws_auth/auth.py) which behaves identically to httpx.Auth where the only difference is the signature of the request and response objects that are sent to and returned from the flow generator respectively. Most HTTPX auth flows can be easily adapted to work with ws_auth
### Kerberos
Alot of PI Web API servers are secured behind Kerberos. [async_negotiate_sspi](https://github.com/newvicx/async_negotiate_sspi) has both an HTTP and Websocket auth flow for single-sign-on on Windows systems. [httpx_gssapi](https://github.com/pythongssapi/httpx-gssapi) is another negotiate auth handler that relies on GSSAPI. It will only work for HTTP requests but it can be easily ported to work for websockets.

## JSON Normalization
Responses from the PI Web API can be deeply nested and somewhat difficult to normalize. Normalizing JSON is usually required if you want to use the data from the PI Web API in a dataframe library like Pandas; in fact Pandas offers a [JSON normalization method](https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html) for converting nested JSON into a dataframe. This works well in a lot of cases but it tends to struggle with non uniform levels, for example take the following response...
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

Converting this response to a dataframe with the `.json_normalize` method will not create a "Name" and "Value" column. It will only have a "Value" column where each row is dict with keys "Name" and "Value".

piwebasync provides a method for normalizing JSON through the `.select()` method on all APIResponse objects. The select method takes an arbitrary number of `*fields` and recursively extracts the all values matching the field into a list. The syntax for a field is identical to the `selectedFields` parameter in most PI Web API methods so you will need to know the schema of the response you expect back. In practice though this isn't a huge burden as the response schemas are well documented and usually you need to something about the response schema to do any meaningful analysis with the data. For identical fields in nested lists (such is the case with streamset responses), the values are grouped by the sub list reside in ultimately returning a list of lists. Consider the example below...

Take the following response where obj 1 and obj 2 represent 2 unique PI points or AF attributes...
```json
{
"Items": [
	{
	"Obj": 1,
	"Items": [
		{"Value": 1},
		{"Value": 2},
	]
	},
	{
	"Obj": 2,
	"Items": [
		{"Value": 3},
		{"Value": 4},
	]
	}
]
}
```

What we probably want is dataframe that looks like this...
|  Obj 1  |  Obj 2 |
|:-------:|:------:|
| Value 1 | Value 3|
| Value 2 | Value 4|

We could normalize the JSON response like so...
```python
selection = response.select("Items.Obj", "Items.Items.Value")
```

This will produce a dictionary object that looks like this...
```python
{
	"Items.Obj": [1, 2],
	"Items.Items.Value": [[1, 2], [3, 4]]
}
```

From the above it is trivial to convert that to a structure which can be directly converted to a dataframe...
```python
desired_struct = {obj: values for obj, values in zip(selection["Items.Obj"], selection["Items.Items.Value"])}
df = pd.DataFrame.from_dict(desired_struct)
```

