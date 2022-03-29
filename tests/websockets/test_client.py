import asyncio
import os

import pytest
from async_negotiate_sspi import NegotiateAuth, NegotiateAuthWS
from dotenv import load_dotenv

from piwebasync import Controller, HTTPClient, WebsocketClient, WebsocketMessage
from piwebasync.exceptions import ChannelClosedError, ChannelClosedOK, ChannelUpdateError, ChannelRollback


"""
Fucntional tests for WebsocketClient. These tests can be run from pytest

Requirements to Run
    - pytest and pytest.asyncio
    - Active and accessible PI Web API server
    - .env file in the root of the \\tests folder that references
    the appropriate variables below
    - Correct authentication flow for your servers authentication
"""


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

@pytest.mark.asyncio
async def test_channel_operation():
    """Test core function of Channel class"""
    webid = await get_tag_webid(PI_POINT)
    request = Controller(
        scheme=WS_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True)
    async with WebsocketClient(request, auth=ws_auth) as channel:
        response = await channel.recv()

    assert isinstance(response, WebsocketMessage)
    assert channel.is_closed


@pytest.mark.asyncio
async def test_channel_iteration():
    """Test channel can be used in an async iterator"""
    webid = await get_tag_webid(PI_POINT)
    request = Controller(
        scheme=WS_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True, heartbeat_rate=2)
    responses = []
    async with WebsocketClient(request, auth=ws_auth) as channel:
        async for response in channel:
            responses.append(response)
            if len(responses) >= 2:
                break
    assert channel.is_closed
    assert len(responses) >= 2
    for response in responses:
        assert isinstance(response, WebsocketMessage)


@pytest.mark.asyncio
async def test_channel_update_success():
    """
    Test channel can be updated without receiver failing
    
    Note: Pytest raises warnings in this test originating from
    the websockets.WebsocketCommonProtocol. The test works as
    expected and when run manually without pytest, no warnings are
    raised. This might have to do with the way pytest handles
    the event loop.
    """
    loop = asyncio.get_event_loop()
    webid_1 = await get_tag_webid(PI_POINT)
    controller = Controller(scheme=WS_SCHEME, host=PI_HOST, root=ROOT)
    request_1 = controller.streams.get_channel(webid_1, include_initial_values=True, heartbeat_rate=2)
    webid_2 = await get_tag_webid(UPDATE_PI_POINT)
    request_2 = controller.streams.get_channel(webid_2, include_initial_values=True, heartbeat_rate=2)
    async with WebsocketClient(request_1, auth=ws_auth, loop=loop) as channel:
        receive_task = loop.create_task(receiver(channel))
        await asyncio.sleep(4)
        await channel.update(request_2)
        assert not receive_task.done()
        await asyncio.sleep(4)
    
    assert channel.is_closed
    # ChannelClosedOK should be raised so receiver returns responses
    responses: list = await receive_task
    merged = responses.pop(0)
    for response in responses:
        merged.items.extend(response.items)
    selection = merged.select("Items.WebId")
    assert webid_1 in selection["Items.WebId"]
    assert webid_2 in selection["Items.WebId"]


@pytest.mark.asyncio
async def test_channel_update_failure():
    """
    Test failed update raises ChannelUpdateError and receiver task raises
    ChannelClosedError
    """
    loop = asyncio.get_event_loop()
    webid = await get_tag_webid(PI_POINT)
    request_1 = Controller(
        scheme=WS_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True, heartbeat_rate=2)
    request_2 = Controller(
        scheme=WS_SCHEME,
        host="mybadhost.com",
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True, heartbeat_rate=2)
    async with WebsocketClient(request_1, auth=ws_auth, loop=loop) as channel:
        receive_task = loop.create_task(receiver(channel))
        await asyncio.sleep(1)
        try:
            with pytest.raises(ChannelUpdateError):
                await channel.update(request_2)
        except ChannelUpdateError:
            pass
        try:
            with pytest.raises(ChannelClosedError):
                await receive_task
        except ChannelClosedError:
            pass
    assert channel.is_closed


@pytest.mark.asyncio
async def test_channel_rollback():
    """
    Test failed failed update with rollback enabled raises ChannelRollback
    and channel continues to process messages at old endpoint
    """
    loop = asyncio.get_event_loop()
    webid = await get_tag_webid(PI_POINT)
    request_1 = Controller(
        scheme=WS_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True, heartbeat_rate=2)
    request_2 = Controller(
        scheme=WS_SCHEME,
        host="mybadhost.com",
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True, heartbeat_rate=2)
    async with WebsocketClient(request_1, auth=ws_auth, loop=loop) as channel:
        receive_task = loop.create_task(receiver(channel))
        await asyncio.sleep(1)
        
        with pytest.raises(ChannelRollback):
            await channel.update(request_2, rollback=True)
        
        await asyncio.sleep(1)
        assert not receive_task.done()
        assert not channel.is_closed
        assert channel.is_open