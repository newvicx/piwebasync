import asyncio
import logging
import os

from async_negotiate_sspi import NegotiateAuth, NegotiateAuthWS
from dotenv import load_dotenv

from piwebasync import Controller, HTTPClient, WebsocketClient


"""
Test watchdog logic by simulating a network interruption that
does not recover

Requirements to Run
    - Active and accessible PI Web API server
    - .env file in the root of the \\tests folder that references
    the appropriate variables below
    - Correct authentication flow for your servers authentication

Procedure
    - Run file as __main__
    - Once channel is open. Disable all network adapters on local
    machine
    - Confirm channel is trying to reconnect by examining logs
    - Wait for WatchdogTimeout error to be raised. This should take
    about 10 seconds but could take longer if socket does not close
    immediately and underlying websocket fails on ping timeout
    - Test passes when WatchdogTimeout error is raised
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


async def test_watchdog():
    webid = await get_tag_webid(PI_POINT)
    request = Controller(
        scheme=WS_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True)
    async with WebsocketClient(request, auth=ws_auth, reconnect=True, dead_channel_timeout=10) as channel:
        async for response in channel:
            logger.info("Received response: Items - %i", len(response.items))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_watchdog())