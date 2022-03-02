# Advanced Usage

## Websockets

The `WebsocketClient` was built with data streaming services in mind. Lets explore some of the more advanced features by building a pseudo code concept for a simple streaming service.

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

async def publisher_task(queue: asyncio.Queue):
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
        publish_task = loop.create_task(publisher_task(queue))
        tasks = [receive_task, publish_task]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
	asyncio.run(main())
```

So this covers our first two requirements...

> - Opens a websocket connection to a channel endpoint
> 
> - Continuously receives data from the channel, extracts the required information and passes the message to a message broker

There are some problems though. What happens if we experience a network interruption or protocol error? Well first, `receive_task` will continue to get messages from the channel so long as messages are buffered. But, once the buffer is exhausted, it will raise a `ChannelClosedError` as a result of thenetwork error and the service will crash. Our requirements say the service should...

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
            raise err.__cause__
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
        tasks = [receive_task, publish_task]
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_EXCEPTION
        )
        for task in pending:
            task.cancel()
        try:
            await asyncio.gather(*done)
        except WatchdogTimeout:
            # Notify admin
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
async def listener_task(channel: WebsocketClient):
    consumer = broker_connection(connect_url, role="consumer")
    try:
        while True:
            new_request = await consumer.get()
            try:
            	await channel.update(new_request)
            except ChannelUpdateError:
                await consumer.close()
                raise
    except asyncio.CancelledError:
        await consumer.close()
        raise
```

Then we will update `main` to add this task and handle `ChannelUpdateError`...

```python
async def main():
    loop = asyncio.get_event_loop()
    request = Controller(scheme, host, root=root).streams.get_channel(webid)
    queue = asyncio.Queue()
	async with WebsocketClient(request, auth=NegotiateAuthWS()) as channel:
        receive_task = loop.create_task(receive_new_data_task(channel, queue))
        publish_task = loop.create_task(publish_task(queue))
        listen_task = loop.create_task(listener_task(channel))
        tasks = [receive_task, publish_task, listen_task]
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_EXCEPTION
        )
        for task in pending:
            task.cancel()
        try:
            await asyncio.gather(*done)
        except WatchdogTimeout:
            # Notify admin
            raise
        except ChannelUpdateError:
            # Notify user they broke something
            raise
```

And finally we have our concept that meets our requirements...

```python
import asyncio
from async_negotiate_sspi import NegotiateAuthWS
from piwebasync import Controller, WebsocketClient
from piwebasync.exceptions import ChannelClosedError, 
from broker_service import broker_connection

async def listener_task(channel: WebsocketClient):
    consumer = broker_connection(connect_url, role="consumer")
    try:
        while True:
            new_request = await consumer.get()
            try:
            	await channel.update(new_request)
            except ChannelUpdateError:
                await consumer.close()
                raise
    except asyncio.CancelledError:
        await consumer.close()
        raise
        
async def publisher_task(queue: asyncio.Queue):
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
    try:
        async for message in channel:
            publish_message = message.select("Items.Name", "Items.Items.Timestamp", "Items.Items.Value")
            await queue.put(publish_message)
    except ChannelClosedError as err:
        if isinstance(err.__cause__, WatchdogTimeout):
            raise err.__cause__
        raise
        
async def main():
    loop = asyncio.get_event_loop()
    request = Controller(scheme, host, root=root).streams.get_channel(webid)
    queue = asyncio.Queue()
	async with WebsocketClient(request, auth=NegotiateAuthWS()) as channel:
        receive_task = loop.create_task(receive_new_data_task(channel, queue))
        publish_task = loop.create_task(publisher_task(queue))
        listen_task = loop.create_task(listener_task(channel))
        tasks = [receive_task, publish_task, listen_task]
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_EXCEPTION
        )
        for task in pending:
            task.cancel()
        try:
            await asyncio.gather(*done)
        except WatchdogTimeout:
            # Notify admin
            raise
        except ChannelUpdateError:
            # Notify user they broke something
            raise
```

***Note: The above code is just for demonstrating the topics discussed in this section and should NOT be adapted for production use***

## Selecting Response Subset and JSON Normalization

Responses from the PI Web API can be deeply nested and somewhat difficult to normalize. Normalizing JSON is usually required if you want to use the data from the PI Web API in a dataframe library

### Pandas

Pandas is the most popular python dataframe library out there and it offers a [JSON normalization method](https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html) for converting nested JSON into a dataframe. This works well in a lot of cases. For example, take the following response...

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
The following code will be used to generate each output...

```python
import orjson
import pandas as pd
out = pd.json_normalize(response.dict()["Items"])
```

```
>>> out
              Timestamp UnitsAbbreviation  Good  Questionable  Substituted  Annotated Value.Name  Value.Value
0  2014-07-22T14:00:00Z                 m  True         False        False      False        Off            0
1  2014-07-22T14:00:00Z                 m  True         False        False      False        Off            0
```

Worked great! But, it falls short in other cases. Take this response...

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

```
>>> out
              Timestamp UnitsAbbreviation  Good  Questionable  ...  Annotated  Value           Value.Name Value.Value
0  2014-07-22T14:00:00Z                 m  True         False  ...      False    0.0                  NaN         NaN
1  2014-07-22T14:00:00Z                 m  True         False  ...      False    NaN  Interface Bad Value        -1.0
```

Notice how we have two "Value" columns each with half of what we're looking for. Ideally we want a single column with both values.

Finally, it just completely breaks down in some cases. This is an example of streamset response...

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

```
>>> out["Items"]
0    [{'Timestamp': '2014-07-22T14:00:00Z', 'UnitsA...
1    [{'Timestamp': '2014-07-22T14:00:00Z', 'UnitsA...

```

We would need to create two separate dataframes and merge them in order to get a sensible output.

### APIResponse.select()

piwebasync provides a method for normalizing JSON through the `.select()` method on all `APIResponse` objects. The `.select()` method takes an arbitrary number of `*fields` and recursively extracts all values matching the field into a list. The syntax for a field is identical to the `selectedFields` parameter in most PI Web API methods (i.e. dot notation). Identical field keys across different lists in the JSON response will be aggregated into a list of lists. The [API Reference](https://github.com/newvicx/piwebasync/blob/main/docs/API%20Reference.md) has in depth examples using the `.select()` method. In this section, we will just compare its use to Pandas.

Lets work with the streamset response output from above. What we probably want is to produce a dataframe like this...
| Water | Fire |
| :---: | :--: |
| 12.3  | 451  |
| 12.3  | 451  |

We could select from and normalize the JSON response in one go like so...
```python
selection = response.select("Items.Name", "Items.Items.Value")
```

This will produce a dictionary object that looks like this...
```python
{
	"Items.Name": ["Water", "Fire"],
	"Items.Items.Value": [[12.3, 12.3], [451, 451]]
}
```

You can convert this output to a dataframe like so...
```python
desired_struct = {name: values for name, values in zip(selection["Items.Name"], selection["Items.Items.Value"])}
df = pd.DataFrame.from_dict(desired_struct)
```

And the output...

```
>>> out
   Water  Fire
0   12.3   451
1   12.3   451
```

## Error Handling in Responses

### Status Code

The status code is the easiest way to tell if a response was successful or not. You can access the status code directly on any `HTTPResponse` object

```python
print(response.status_code)
```

`WebsocketMessage` objects do not have a status code

### Web Exception 

From the PI Web API reference

> Introduced in PI Web API 2017 R2, PI Web API now exposes a 'WebException' property on **all** controller responses.
>
> Any PI Web API response containing a 'WebException' property which is non-null indicates that PI Web API encountered an **unhandled** error during the transfer of the response stream. These errors can occur despite PI Web API responding with a successful HTTP status code. Responses will not contain a 'WebException' if no error occurred. When present, the 'WebException' property will be present at the top level of all response objects. A 'WebException' contains a 'StatusCode' field, which indicates the correct error HTTP Status Code the client should interpret the response as returning with.

All `APIResponse` objects handle the WebException property and will alter the status code of a response should it be required

You can check if response has a WebException using the `dict()` method

```python
has_web_exception = response.dict().get("WebException") is not None
```

### Errors

The body of a response with a 400- or 500- level status code can have an "Errors" property. You can check for this in a similar manner to the "WebException" property

```python
has_errors = response.dict().get("Errors") is not None
```

Errors in the response body can also occur due to a `JSONDecodeError` when either the `HTTPClient` or `WebsocketClient` is handling the raw response content. These errors will be associated with a "ResponseContent" and "ErrorMessage" property in the APIResponse content. Similar to the cases above you can check for this type of error like so...

```python
has_parsing_error = response.dict().get("ResponseContent") is not None
# OR
has_parsing_error = response.dict().get("ErrorMessage") is not None
```

There is an additional error that can occur in the Stream and StreamSet controllers. From the PI Web API Reference...

> The Stream and Stream Set controller responses may contain an additional field called 'Errors' in the response. The purpose of the 'Errors' field is to indicate that an error occurred for a particular value while streaming the response. For example, if there are 100 values returned and one of them has an associated error, the remaining 99 values do not need to be discarded. Values will not contain an 'Errors' property if no error occurred. Each object in the list of 'Errors' contains which field name caused an error, as well as the exception message.
>
> Unlike 'WebException', which is a single property found at the top level of the response object, an 'Errors' property may be present on any stream value. If a stream value contains an 'Errors' property then its value will be 'null'. If any stream values in the response contain an 'Errors' field, that does not mean the entire value collection returned is invalid.
>
> Example Response Body:
>
> ```json
> {
>     "Timestamp": "2014-07-22T14:00:00Z",
>     "UnitsAbbreviation": null,
>     "Good": true,
>     "Questionable": false,
>     "Substituted": false,
>     "Value": null,
>     "Errors": [
>         {
>             "FieldName": "UnitsAbbreviation",
>             "Message": [
>                 "PI Point not found."
>             ]
>         },
>         {
>             "FieldName": "Value",
>             "Message": [
>                 "PI Point not found."
>             ]
>         }
>     ]
> }
> ```

At this time you cannot check for these errors directly. You can use `.select()` to search for the "Errors" property in the response content but, if for example, it only occurs in 2/100 records in the response content you will get an output that looks like this...

```python
{
    "Items.Value": [v1, ..., v100],
    "Items.Errors": [e1, e2]
}
```

In other words, you will not be able to associate the error to record where it occurred. However, any value where an error occurred is guaranteed to be `null` so in most cases you can just disregard the value and log the errors so you know they occurred.
