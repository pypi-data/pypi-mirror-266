##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\exceptions.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_exceptions.py

import pytest
from unittest.mock import MagicMock
from aiohttp import ClientResponse
from openaiwrapper.exceptions import OpenAIRequestError, create_openai_request_error, log_openai_request_error

@pytest.mark.asyncio
async def test_create_openai_request_error_with_json():
    # Mock aiohttp.ClientResponse
    response = MagicMock(spec=ClientResponse)
    response.status = 400
    response.headers = {'X-Request-ID': 'test-request-id'}
    response.json = MagicMock(return_value={
        'error': {'message': 'Test error message', 'type': 'TestError'}
    })

    error = await create_openai_request_error(response)
    assert error.message == 'Test error message'
    assert error.status_code == 400
    assert error.error_type == 'TestError'
    assert error.request_id == 'test-request-id'

@pytest.mark.asyncio
async def test_create_openai_request_error_with_text():
    # Mock aiohttp.ClientResponse for non-JSON response
    response = MagicMock(spec=ClientResponse)
    response.status = 500
    response.headers = {'X-Request-ID': 'test-request-id'}
    response.json = MagicMock(side_effect=Exception("ContentTypeError"))
    response.text = MagicMock(return_value='Test error text')

    error = await create_openai_request_error(response)
    assert error.message == 'Test error text'
    assert error.status_code == 500
    assert error.error_type == 'ContentTypeError'
    assert error.request_id == 'test-request-id'

@pytest.mark.asyncio
async def test_log_openai_request_error(mocker):
    mocker.patch('openaiwrapper.exceptions.logger')
    error = OpenAIRequestError(
        message='Test logging',
        status_code=404,
        error_type='NotFoundError',
        request_id='test-log-request-id'
    )

    log_openai_request_error(error)
    # Verify logger.error was called with the expected message
    from openaiwrapper.exceptions import logger
    logger.error.assert_called_with(
        "OpenAIRequestError encountered: NotFoundError - Test logging "
        "(Status code: 404, Request ID: test-log-request-id)"
    )
