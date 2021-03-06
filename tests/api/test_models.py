import pytest
from httpx import Headers
from pydantic import ValidationError

from piwebasync.api import APIRequest, APIResponse, Controller, HTTPResponse
from piwebasync.exceptions import HTTPStatusError


HTTP_SCHEME = "http"
WS_SCHEME = "ws"
HOST = "mypihost.com"
ROOT = "piwebapi"
PORT = 80
WEBID = "mytestwebid"


class TestController:
    def test_chaining(self):
        """Create request in single call"""
        expected = f"{HTTP_SCHEME}://{HOST}:{PORT}/{ROOT}/streams/{WEBID}/end"
        request = Controller(
            HTTP_SCHEME,
            HOST,
            PORT,
            ROOT
        ).streams.get_end(WEBID)
        assert request.absolute_url == expected


    def test_reuse_base(self):
        """Reuse base url of controller"""
        controller = Controller(
            HTTP_SCHEME,
            HOST,
            PORT,
            ROOT
        )
        expected = f"{HTTP_SCHEME}://{HOST}:{PORT}/{ROOT}/streams/{WEBID}/end"
        request = controller.streams.get_end(WEBID)
        assert request.absolute_url == expected

        expected = f"{HTTP_SCHEME}://{HOST}:{PORT}/{ROOT}/streams/{WEBID}/recorded"
        request = controller.streams.get_recorded(WEBID)
        assert request.absolute_url == expected


    def test_serialize_special_params(self):
        """
        Certain parameters can be specified mutliple times. These paramters have
        special serialization methods depending on what the parameter is
        """
        webid_1 = "webid_1"
        webid_2 = "webid_2"
        expected = f"{HTTP_SCHEME}://{HOST}:{PORT}/{ROOT}/streamsets/end?webId={webid_1}&webId={webid_2}"
        request = Controller(
            HTTP_SCHEME,
            HOST,
            PORT,
            ROOT
        ).streamsets.get_end_adhoc(webid=[webid_1, webid_2])
        assert request.absolute_url == expected

        expected = f"{HTTP_SCHEME}://{HOST}:{PORT}/{ROOT}/streamsets/{WEBID}/end?selectedFields=Items.WebId;Items.Items.Timestamp"
        request = Controller(
            HTTP_SCHEME,
            HOST,
            PORT,
            ROOT
        ).streamsets.get_end(WEBID, selected_fields=["Items.WebId", "Items.Items.Timestamp"])
        assert request.absolute_url == expected


class TestAPIRequest:
    @pytest.mark.parametrize(
        "webid,action,add_path,query,expected",
        [
            (
                "Test",
                "TestAction",
                ["AddPath1", "AddPath2"],
                {"query_1": "Value"},
                "/root/controller/Test/TestAction/AddPath1/AddPath2?query1=Value"
            ),
            (
                None,
                "TestAction",
                ["AddPath1", "AddPath2"],
                {"query_1": "Value"},
                "/root/controller/TestAction/AddPath1/AddPath2?query1=Value"
            ),
            (
                "Test",
                None,
                ["AddPath1", "AddPath2"],
                {"query_1": "Value"},
                "/root/controller/Test/AddPath1/AddPath2?query1=Value"
            ),
            (
                "Test",
                "TestAction",
                None,
                {"query_1": "Value"},
                "/root/controller/Test/TestAction?query1=Value"
            ),
            (
                "Test",
                "TestAction",
                ["AddPath1", "AddPath2"],
                {},
                "/root/controller/Test/TestAction/AddPath1/AddPath2"
            ),
            (
                None,
                None,
                None,
                {},
                "/root/controller"
            ),
        ]
    )
    def test_path_construction(
        self,
        webid,
        action,
        add_path,
        query,
        expected
    ):
        """
        The URL path should follow this schema...
            
            /{root}/{controller}/{webid}/{action}/{add_path}?{query}

        The only required parts of the path are the root and controller.
        All other path parameters can be included or neglected depending
        on the API endpoint spec
        """

        request = APIRequest(
            root="root",
            method="GET",
            protocol="HTTP",
            controller="controller",
            scheme="http",
            host="myhost",
            action=action,
            webid=webid,
            add_path=add_path,
            **query
        )
        assert request.raw_path == expected


    def test_method_validation(self):
        """Test that invalid HTTP method raises ValidationError"""
        with pytest.raises(ValidationError):
            APIRequest(
                root="root",
                method="UPDATE",    # Invalid method
                protocol="HTTP",
                controller="controller",
                scheme="http",
                host="myhost"
            )
        
    def test_protocol_validation(self):
        """Test that invalid protocol raises ValidationError"""
        with pytest.raises(ValidationError):
            APIRequest(
                root="root",
                method="UPDATE",
                protocol="AMQP",    # Invalid protocol
                controller="controller",
                scheme="http",
                host="myhost"
            )


class TestAPIResponse:
    def test_web_exception(self):
        """Test handling of Web Exception in response body"""
        content = {
            "WebException": {
                "Errors": [
                    "Error occurred during writing of the output stream."
                ],
                "StatusCode": 500
            }
        }
        response = APIResponse(
            status_code=200,
            **content
        )
        assert response.status_code == 500
        assert response.errors == ["Error occurred during writing of the output stream."]
    

    def test_response_normalization(self):
        """
        Top level attributes in response body should be normalized to snake case
        """

        content = {
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
            "Step": False,
            "Future": False,
            "DisplayDigits": -5,
            "Links": {
                "Self": "https://localhost.osisoft.int/piwebapi/points/I1DPa70Wf0zBA06CLkV9ovNQgQCAAAAA"
            }
        }
        response = APIResponse(
            **content
        )
        assert response.display_digits == -5

    def test_dict_conversion(self):
        """
        When converting to dict, top level attributes should convert back to camel case
        """
        content = {
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
            "Step": False,
            "Future": False,
            "DisplayDigits": -5,
            "Links": {
                "Self": "https://localhost.osisoft.int/piwebapi/points/I1DPa70Wf0zBA06CLkV9ovNQgQCAAAAA"
            }
        }
        response = APIResponse(
            **content
        )
        assert response.dict()["DisplayDigits"] == -5


def test_http_status_error():
    """
    Unsuccessful status codes or JSON parsing errors should raise
    an HTTPStatusError
    """
    headers = Headers()
    content = {
        "Errors": [
            "The specified path was not found. If more details are needed, please contact your PI Web API administrator for help in enabling debug mode."
        ]
    }
    response = HTTPResponse(
        status_code=404,
        url="https://Test404URL.com",
        headers=headers,
        **content
    )
    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    
    content = {
        "Errors": [
            "Invalid character at line 0"
        ],
        "ResponseContent": "\\",
        "ErrorMessage": "JSONDecodeError: Invalid character at line 0"
    }
    response = HTTPResponse(
        status_code=200,
        url="https://TestUnableToParse.com",
        headers=headers,
        **content
    )
    with pytest.raises(HTTPStatusError):
        response.raise_for_status()

    content = {
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
        "Step": False,
        "Future": False,
        "DisplayDigits": -5,
        "Links": {
            "Self": "https://localhost.osisoft.int/piwebapi/points/I1DPa70Wf0zBA06CLkV9ovNQgQCAAAAA"
        }
    }
    response = HTTPResponse(
        status_code=200,
        url="https://TestSuccess.com",
        headers=headers,
        **content
    )
    response.raise_for_status()
