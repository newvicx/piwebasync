import asyncio
import logging
import os

from async_negotiate_sspi import NegotiateAuth, NegotiateAuthWS
from dotenv import load_dotenv

from piwebasync import Controller, HTTPClient, WebsocketClient


"""
Test reconnect logic by simulating a network interruption

Requirements to Run
    - Active and accessible PI Web API server
    - .env file in the root of the \\tests folder that references
    the appropriate variables below
    - Correct authentication flow for your servers authentication

Procedure
    - Run file as __main__
    - Once channel is open. Disable all network adapters on local
    machine
    - Confirm channel is closed from logs
    - Re-enable network adapters
    - Confirm channel is reconnected from logs
    - Issue a KeyboardInterrupt
    - Test passes when channel is confirmed reconnected and no errors
    have been raised besides KeyboardInterrupt
"""


load_dotenv()

HTTP_SCHEME = os.getenv("HTTP_SCHEME")
WS_SCHEME = os.getenv("WS_SCHEME")
PI_HOST = os.getenv("PI_HOST")
ROOT = os.getenv("ROOT")
DATASERVER = os.getenv("DATASERVER")
PI_POINT = os.getenv("PI_POINT")

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


async def test_reconnect():
    webid = await get_tag_webid(PI_POINT)
    request = Controller(
        scheme=WS_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).streams.get_channel(webid, include_initial_values=True)
    async with WebsocketClient(request, auth=ws_auth, reconnect=True, dead_channel_timeout=None) as channel:
        async for response in channel:
            logger.info("Received response: Items - %i", len(response.items))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_reconnect())