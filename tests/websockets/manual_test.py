import asyncio
import logging
import os

import pytest
from async_negotiate_sspi import NegotiateAuth, NegotiateAuthWS
from dotenv import load_dotenv

from piwebasync import Controller, HTTPClient, WebsocketClient
from piwebasync.exceptions import ChannelClosedError, ChannelClosedOK

load_dotenv()

HTTP_SCHEME = os.getenv("HTTP_SCHEME")
WS_SCHEME = os.getenv("WS_SCHEME")
PI_HOST = os.getenv("PI_HOST")
ROOT = os.getenv("ROOT")
DATASERVER = os.getenv("DATASERVER")
PI_POINT = os.getenv("PI_POINT")
UPDATE_PI_POINT = os.getenv("UPDATE_PI_POINT")

# Use for kerberos or NTLM
http_auth = NegotiateAuth()
ws_auth = NegotiateAuthWS()

logger = logging.getLogger(__name__)

async def get_tag_webid(point: str):
    """Get WebId for test PI tag"""
    tag_path = f"\\\\{DATASERVER}\\{point}"
    request = Controller(
        scheme=HTTP_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).points.get_by_path(tag_path)
    # Make request, select webid
    async with HTTPClient(auth=http_auth, safe_chars="/?:=&%;\\", verify=False) as client:
        response = await client.request(request)
        selection = response.select("WebId")
    return selection["WebId"][0]


async def receiver(channel: WebsocketClient):
    """Receive messages from channel in asyncio.Task"""
    responses = []
    try:
        async for response in channel:
            responses.append(response)
    except ChannelClosedError:
        raise
    except ChannelClosedOK:
        return responses

async def test_channel_update_success():
    """
    Identical to test in test_client but intended to be run
    from interpreter. Warnings are not raised this way
    """
    loop = asyncio.get_event_loop()
    webid_1 = await get_tag_webid(PI_POINT)
    controller = Controller(scheme=WS_SCHEME, host=PI_HOST, root=ROOT)
    request_1 = controller.streams.get_channel(webid_1, include_initial_values=True, heartbeat_rate=2)
    webid_2 = await get_tag_webid(UPDATE_PI_POINT)
    request_2 = controller.streams.get_channel(webid_2, include_initial_values=True, heartbeat_rate=2)
    async with WebsocketClient(request_1, auth=ws_auth) as channel:
        receive_task = loop.create_task(receiver(channel))
        await asyncio.sleep(4)
        await channel.update(request_2)
        assert not receive_task.done()
        await asyncio.sleep(4)
    
    assert channel.is_closed
    # ChannelClosedOK should be raised so receiver returns responses
    responses: list = await receive_task
    logger.debug(f"Num responses = {len(responses)}")
    merged = responses.pop(0)
    for response in responses:
        merged.items.extend(response.items)
    logger.debug(f"Merged {merged}")
    selection = merged.select("Items.WebId")
    assert webid_1 in selection["Items.WebId"]
    assert webid_2 in selection["Items.WebId"]
    logger.debug(f"Selection: {selection}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_channel_update_success())