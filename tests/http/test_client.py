import os

import pytest
from async_negotiate_sspi import NegotiateAuth
from dotenv import load_dotenv

from piwebasync import Controller, HTTPClient


"""
The HTTPClient is a simple wrapper around the ExClient from
httpx_extensions which is fully tested. Therefore the test
here is just simple functional test of sending an HTTP request
along with a test for the safe chars feature

Requirements to Run
    - pytest and pytest.asyncio
    - Active and accessible PI Web API server
    - .env file in the root of the \\tests folder that references
    the appropriate variables below
    - Correct authentication flow for your servers authentication
"""

load_dotenv()

HTTP_SCHEME = os.getenv("HTTP_SCHEME")
PI_HOST = os.getenv("PI_HOST")
ROOT = os.getenv("ROOT")
DATASERVER = os.getenv("DATASERVER")
PI_POINT = os.getenv("PI_POINT")
POINT_WEBID = os.getenv("POINT_WEBID")

# Use for kerberos or NTLM
http_auth = NegotiateAuth()

@pytest.mark.asyncio
async def test_request_and_safe_chars():
    """
    Simple functional test retrieving information on a PI Point. Also
    tests safe chars feature as backslashes are usually percent
    encoded.
    """
    tag_path = f"\\\\{DATASERVER}\\{PI_POINT}"
    request = Controller(
        scheme=HTTP_SCHEME,
        host=PI_HOST,
        root=ROOT
    ).points.get_by_path(tag_path)
    # Make request, select webid
    async with HTTPClient(auth=http_auth, safe_chars="/?:=&%;\\", verify=False) as client:
        response = await client.request(request)
        selection = response.select("WebId")
    assert selection["WebId"][0] == POINT_WEBID
    assert response.url == request.absolute_url