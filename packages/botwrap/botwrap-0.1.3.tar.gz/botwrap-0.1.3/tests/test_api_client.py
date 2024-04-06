##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\api_client.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_api_client.py

import pytest
from aiohttp import web
from openaiwrapper.api_client import OpenAIAPIClient

# Mock server to simulate OpenAI API responses
async def mock_openai_api(request):
    if request.path == '/v1/test-success':
        return web.json_response({"success": True}, status=200)
    elif request.path == '/v1/test-rate-limit':
        return web.Response(status=429, headers={"Retry-After": "1"})
    elif request.path == '/v1/test-server-error':
        return web.Response(status=500)
    # Add more conditional paths as needed for testing

@pytest.fixture
async def mock_server(aiohttp_server):
    app = web.Application()
    app.router.add_route('*', '/v1/{tail:.*}', mock_openai_api)
    server = await aiohttp_server(app)
    return server

@pytest.mark.asyncio
async def test_successful_api_call(mock_server):
    async with OpenAIAPIClient(api_key='test_api_key', base_url=mock_server.make_url('/v1').human_repr()) as client:
        response = await client.make_api_call('test-success', 'GET')
    assert response == {"success": True}

@pytest.mark.asyncio
async def test_rate_limit_handling(mock_server):
    async with OpenAIAPIClient(api_key='test_api_key', base_url=mock_server.make_url('/v1').human_repr()) as client:
        response = await client.make_api_call('test-rate-limit', 'GET')
    assert response == {"success": True}  # This assumes the client is designed to retry after a rate limit error and succeeds

@pytest.mark.asyncio
async def test_server_error_handling(mock_server):
    async with OpenAIAPIClient(api_key='test_api_key', base_url=mock_server.make_url('/v1').human_repr()) as client:
        with pytest.raises(Exception) as exc_info:  # Replace Exception with your specific exception for handling HTTP errors
            await client.make_api_call('test-server-error', 'GET')
    assert '500 Server Error' in str(exc_info.value)  # Check for correct error message
