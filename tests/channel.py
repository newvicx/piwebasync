import asyncio
import logging
import os

import pytest
from async_negotiate_sspi import NegotiateAuth, NegotiateAuthWS
from dotenv import load_dotenv
from httpx import Headers

from piwebasync import Channel, HTTPClient
from piwebasync.api import Points, Streams


load_dotenv()

HTTP_SCHEME = os.getenv("HTTP_SCHEME")
WS_SCHEME = os.getenv("WS_SCHEME")
PI_HOST = os.getenv("PI_HOST")
ROOT = os.getenv("ROOT")
DATASERVER = os.getenv("DATASERVER")
PI_POINT = os.getenv("PI_POINT")

logger = logging.Logger(__name__)

async def get_tag_webid():
    """Get WebId for test PI tag"""
    
    # Build request
    tag_path = f"\\\\{DATASERVER}\\{PI_POINT}"
    tag_resource = Points.get_by_path(tag_path)
    tag_request = tag_resource.build_request(
        scheme=HTTP_SCHEME, host=PI_HOST, root=ROOT
    )
    # Use for kerberos or NTLM
    auth = NegotiateAuth()
    # Make request, select webid
    async with HTTPClient(auth=auth, safe_chars="/?:=&%;\\", verify=False) as client:
        response = await client.request(tag_request)
        selection = response.select("WebId")
    
    return selection["WebId"]

@pytest.mark.asyncio
async def test_channel_operation():
    """Test core function of Channel class"""
    webid = await get_tag_webid()
    resource = Streams.get_channel(webid, include_initial_values=True)
    request = resource.build_request(
        scheme=WS_SCHEME, host=PI_HOST, root=ROOT
    )
    auth = NegotiateAuthWS()
    logger.warning(f"{request.absolute_url}")
    async with Channel(request, auth=auth) as channel:
        await asyncio.sleep(1)
        #response = await asyncio.wait_for(channel.recv(), 1)
    assert response.Items is not None
    

@pytest.mark.asyncio
async def test_channel_iteration():
    """Test channel can be used in an async iterator"""
    webid = await get_tag_webid()
    resource = Streams.get_channel(
        webid,
        include_initial_values=True,
        heartbeat_rate=1
    )
    request = resource.build_request(
        scheme=WS_SCHEME, host=PI_HOST, root=ROOT
    )
    auth = NegotiateAuthWS()
    num_responses = 0
    async with Channel(request, auth=auth) as channel:
        async for response in channel:
            num_responses += 1
            if num_responses >= 2:
                break
    assert num_responses == 2


# @pytest.mark.asyncio
async def test_channel_update():
    webid = await get_tag_webid()
    resource = Streams.get_channel(webid, include_initial_values=True)
    request = resource.build_request(
        scheme=WS_SCHEME, host=PI_HOST, root=ROOT
    )
    auth = NegotiateAuthWS()
    async with Channel(request, auth=auth) as channel:
        response_1 = await channel.recv()
        await channel.update(request)
        response_2 = await channel.recv()
    
    assert response_1.url == response_2.url


# @pytest.mark.asyncio
async def test_channel_reconnect():
    from websockets.exceptions import ConnectionClosedError
    webid = await get_tag_webid()
    resource = Streams.get_channel(
        webid,
        include_initial_values=True,
        heartbeat_rate=1
    )
    request = resource.build_request(
        scheme=WS_SCHEME, host=PI_HOST, root=ROOT
    )
    auth = NegotiateAuthWS()
    num_responses = 0
    async with Channel(request, auth=auth, reconnect=True) as channel:
        async for response in channel:
            num_responses += 1
            if num_responses == 1:
                # The shutdown waiter would never throw this
                # but its a good way to simulate the error
                # that triggers a reconnect
                channel._shutdown_waiter.set_exception(
                    ConnectionClosedError
                )
            if num_responses == 2:
                break
    assert num_responses == 2