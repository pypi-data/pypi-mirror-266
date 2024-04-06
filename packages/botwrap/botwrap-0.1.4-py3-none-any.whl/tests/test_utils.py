##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\utils.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_utils.py

import pytest
import json
from unittest.mock import MagicMock
from openaiwrapper.utils import handle_http_error, log_api_call, validate_response_content_type, format_data_for_request, validate_list_of_dicts, datetime_to_iso, sanitize_input, fetch_all_pages
from openaiwrapper.exceptions import OpenAIRequestError
from aiohttp import ClientResponse
from datetime import datetime

@pytest.mark.asyncio
async def test_handle_http_error_400():
    response = MagicMock(spec=ClientResponse)
    response.status = 400
    response.json = MagicMock(return_value={'error': {'message': 'Test Error', 'type': 'TestType'}})
    response.headers = {'X-Request-ID': 'test-request-id'}
    
    with pytest.raises(OpenAIRequestError) as exc_info:
        await handle_http_error(response)
    
    assert exc_info.value.message == 'Test Error'
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == 'TestType'
    assert exc_info.value.request_id == 'test-request-id'

def test_log_api_call(mocker):
    mocker.patch('openaiwrapper.utils.logger')
    from openaiwrapper.utils import logger

    log_api_call(method='POST', url='/test-url', status_code=200, duration=0.123, data={'key': 'value'})
    logger.info.assert_called_once()
    args, _ = logger.info.call_args
    log_data = json.loads(args[0])
    assert log_data['method'] == 'POST'
    assert log_data['url'] == '/test-url'
    assert log_data['status_code'] == 200
    assert log_data['duration'] == '0.12s'
    assert log_data['data'] == {'key': 'value'}

def test_validate_response_content_type():
    response = MagicMock(spec=ClientResponse)
    response.headers = {'Content-Type': 'application/json'}
    
    # Should not raise
    validate_response_content_type(response, expected_content_type='application/json')
    
    # Should raise due to mismatch
    with pytest.raises(ValueError):
        validate_response_content_type(response, expected_content_type='text/plain')

def test_format_data_for_request():
    data = {'key1': 'value1', 'key2': None}
    formatted_data = format_data_for_request(data)
    assert formatted_data == {'key1': 'value1'}

def test_validate_list_of_dicts():
    items = [{'key1': 'value1', 'key2': 'value2'}, {'key1': 'value3', 'key2': 'value4'}]
    assert validate_list_of_dicts(items, required_keys=['key1', 'key2']) is True
    assert validate_list_of_dicts(items, required_keys=['key1', 'key3']) is False

def test_datetime_to_iso():
    dt = datetime(2020, 1, 1, 12, 0)
    assert datetime_to_iso(dt) == '2020-01-01T12:00:00'

def test_sanitize_input():
    assert sanitize_input("  test string  ") == "test string"

@pytest.mark.asyncio
async def test_fetch_all_pages(mocker):
    async def mock_fetch_page_function(page_token=None, **params):
        if page_token == 'token1':
            return [{'id': 'item3'}], None
        return [{'id': 'item1'}, {'id': 'item2'}], 'token1'

    all_items = await fetch_all_pages(mock_fetch_page_function)
    assert len(all_items) == 3
    assert all_items[0]['id'] == 'item1'
    assert all_items[1]['id'] == 'item2'
    assert all_items[2]['id'] == 'item3'
