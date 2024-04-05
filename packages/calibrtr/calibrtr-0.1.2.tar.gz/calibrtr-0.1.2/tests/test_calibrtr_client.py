import unittest
from unittest import mock
from calibrtr import CalibrtrClient

expected_deployment_id = "XX_YY_ZZ"
expected_api_key = "AA_BB_CC"

expected_request = {
    "prompt" : "foo",
    "context" : "bar"
}

expected_response = {
    "response" : "baz"
}


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

    url = args[0]
    assert url == f"https://calibrtr.com/api/v1/deployments/{expected_deployment_id}/logusage"
    headers = kwargs.get('headers')
    data = kwargs.get('json')
    assert headers['x-api-key'] == expected_api_key
    assert data['aiProvider'] == "ai_provider"
    assert data['aiModel'] == "ai_model"
    assert data['system'] == "system"
    assert data['requestTokens'] == 7
    assert data['responseTokens'] == 9
    assert data['feature'] is None
    assert data['user'] is None
    assert data['request'] is expected_request
    assert data['response'] is expected_response

    return MockResponse(200)


class TestCalibrtrClient(unittest.TestCase):
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_log_usage(self, mock_post):
        client = CalibrtrClient(expected_deployment_id, expected_api_key)
        client.log_usage("ai_provider",
                         "ai_model",
                         "system",
                         7,
                         9,
                         request=expected_request,
                         response=expected_response)
