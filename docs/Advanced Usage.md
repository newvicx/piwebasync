# Advanced Usage

## Websockets

The PI Web API supports the Websocket protocol through the GetChannel method on the Streams and Streamsets controllers. piwebasync provides a websocket client for connecting to and managing websocket connections. This is typically used in streaming or event generation use cases and the WebsocketClient was built these applications in mind

### WebsocketClient

The WebsocketClient class is wrapper around a websockets.Connect instance. Its API closely mimics the Websockets API

The preferred method for opening a websocket connection is with an async context manager...
`import asyncio`
`from piwebasync import Controller, WebsocketClient`

`async def main():`
	`request = Controller(scheme, host, root=root).streams.get_channel(webid)`
	`async with WebsocketClient(request) as channel:`
		`async for response in channel:`
			`print(response.items)`

`if __name__ == "__main__":`
	`asyncio.run(main())`

Refer to the API Reference for the all the methods and parameter for the WebsocketClient. The API should be familiar to those who have used Websockets in the past

Looking at the above example, it will run forever so long as the websocket connection remains open. What happens though if we experience a network interruption or protocol error?. You can continue to consume messages on a closed channel so long as new messages exist in the buffer. As soon as the buffer is exhausted, a `ChannelClosed` exception will be raised. More specifically, if the connection did crash unexpectedly, a `ChannelClosedError` will be raised (this is how the WebsocketClientProtocol works as well).

But lets imagine we are creating a data streaming API that will ingest PI data, perform some logic on the data stream, and generate an event if certain conditions are met (maybe as an API call to some data orchestration service). If there is a network interruption we don't want to the service to crash entirely. This is where reconnects come in.

### Reconnects

You can specify `reconnect=True` in the WebsocketClient constructor and if there is a network interruption or protocol error; rather than raising an error once the buffer is exhausted, the client will attempt to reopen the channel in the background. We can modify the previous example to support reconnects like so...

`import asyncio`
`from piwebasync import Controller, WebsocketClient`

`async def main():`
	`request = Controller(scheme, host, root=root).streams.get_channel(webid)`
	`async with WebsocketClient(request, reconnect=True) as channel:`
		`async for response in channel:`
			`print(response.items)`

`if __name__ == "__main__":`
	`asyncio.run(main())`

Now, if a network interruption occurs, an error wont be raised. Instead the program will wait until the channel re-opens and then continue receiving messages as if the interruption never occurred.

But (there's always a but...) if we are running a data streaming service and the PI server experiences a long outage we don't want to be constantly trying to reconnect with no warning whatsoever. We probably want an error to be raised after a certain amount of time if we are unable to reconnect. The WebsocketClient has a built in watchdog for this purpose.

### Watchdog (dead_channel_timeout)

You can specify a `dead_channel_timeout` (in seconds) in the WebsocketClient constructor. If `reconnect=True` a watchdog task will run in the background and monitor when the channel disconnects. It will wait `dead_channel_timeout` seconds for the connection to be re-opened and if the channel doesn't re-open, the watchdog will close the channel and raise a `WatchdogTimeout` exception. An important thing to note is that you typically will not catch a `WatchdogTimeout` exception directly. Instead, you will catch a `ChannelClosedError` and the `__cause__` will be due to a `WatchdogTimeout`. Lets see an example...

`import asyncio`
`from piwebasync import Controller, WebsocketClient`
`from piwebasync.exceptions import ChannelClosedError, WatchdogTimeout`

`async def main():`
	`request = Controller(scheme, host, root=root).streams.get_channel(webid)`
	`try:`
		`async with WebsocketClient(request, reconnect=True) as channel:`
			`async for response in channel:`
				`print(response.items)`
	`except ChannelClosedError as err:`
		`if isinstance(err.__cause__, WatchdogTimeout):`
			`# notify admin`
			`raise`

`if __name__ == "__main__":`
	`asyncio.run(main())`

Using a `dead_channel_timeout` can help you get notified of some issue with the PI Web API Server that could affect your service.

### Updating the Client Endpoint

Consider this scenario, your service is running great and you're streaming all the data you need. All of sudden you have a new PI tag or AF element that you want to stream data for. There are some naïve options...

1. You can open a new websocket connection that streams just that point or element
2. You can update the config file where you specified all the points/elements and restart the streaming service picking up the new config

The problem with option 1 is that its probably not a good idea to open connections for single points. It's not an efficient use of that connection.

With option 2 we are interrupting the service and if the buffer has unconsumed messages those message will be lost

A better approach would be to modify the existing endpoint and re-open the connection with the modified endpoint. Ideally this should allow us to continue to consume existing messages from the buffer and any new messages will reflect the new query. For this, we would use the `.update()` method.

Lets continue to work with our previous example but add the ability to update the channel in real time. We are going to use some pseudo code to highlight the feature...

`import asyncio`
`from piwebasync import APIRequest, Controller, WebsocketClient`
`from piwebasync.exceptions import ChannelClosedError, ChannelUpdateError, WatchdogTimeout`

`async def receive_task(channel: WebsocketClient):`
    `async for message in channel:`
    	`print("Got a message")`
    	
`async def update_listener_task(channel: WebsocketClient):`
	`listener = await messaging_service.connect("connect_url")`
	`async for update_details in listener:`
		`# We decided to update the channel by sending a message through the messaging service`
		`request = APIRequest(**update_details)`
		`await channel.update(request)`

`async def main():`
	`loop = asyncio.get_event_loop()`
	`request = Controller(scheme, host, root=root).streams.get_channel(webid)`
	`try:`
		`async with WebsocketClient(request, reconnect=True) as channel:`
			`receive_task = loop.create_task(receive_task(channel))`
			`listener_task = loop.create_task(listener_task(channel))`
			`await asyncio.wait([receive_task, listener_task], return_when=asyncio.FIRST_COMPLETED)`
			`if receive_task.done() and not listener_task.done():`
				`try:`
					`await receive_task`
				`except ChannelClosedError:`
					`if isinstance(err.__cause__, WatchdogTimeout):`
                        `# notify admin`
                        `listener_task.cancel()`
                        `raise`
			`await asyncio.gather(receive_task, listener_task)`
	`except (ChannelClosedError, ChannelUpdateError) as err:`
		`raise`

`if __name__ == "__main__":`
	`asyncio.run(main())`

*Note: This is a lot pseudo code with improper error handling. It is simply a demonstration of the concept*

## Authentication

