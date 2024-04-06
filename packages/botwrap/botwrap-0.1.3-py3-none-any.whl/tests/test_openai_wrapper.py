##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\openai_wrapper.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_openai_wrapper.py


import pytest
from unittest.mock import AsyncMock, patch
from openaiwrapper.openai_wrapper import OpenAIWrapper
from openaiwrapper.exceptions import OpenAIRequestError

@pytest.fixture
def mock_api_client():
    return AsyncMock()

@pytest.fixture
def openai_wrapper(mock_api_client):
    with patch('openaiwrapper.openai_wrapper.OpenAIAPIClient', return_value=mock_api_client):
        return OpenAIWrapper(api_client=mock_api_client)

@pytest.mark.asyncio
async def test_create_assistant_success(openai_wrapper):
    openai_wrapper.assistants.create = AsyncMock(return_value={'id': 'assistant-id'})
    response = await openai_wrapper.create_assistant(name="Test Assistant")
    assert response == {'id': 'assistant-id'}
    openai_wrapper.assistants.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_assistant_success(openai_wrapper):
    openai_wrapper.assistants.delete = AsyncMock(return_value=True)
    response = await openai_wrapper.delete_assistant('assistant-id')
    assert response is True

@pytest.mark.asyncio
async def test_list_assistants_failure(openai_wrapper):
    openai_wrapper.assistants.list = AsyncMock(side_effect=OpenAIRequestError(message="API error"))
    with pytest.raises(OpenAIRequestError):
        await openai_wrapper.list_assistants()

@pytest.mark.asyncio
async def test_update_assistant_error_handling(openai_wrapper):
    openai_wrapper.assistants.update = AsyncMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(Exception) as exc_info:
        await openai_wrapper.update_assistant('assistant-id', name="Updated Assistant")
    assert "Unexpected error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_thread_success(openai_wrapper):
    openai_wrapper.threads.create = AsyncMock(return_value={'id': 'thread-id'})
    response = await openai_wrapper.create_thread()
    assert response == {'id': 'thread-id'}

@pytest.mark.asyncio
async def test_delete_thread_error_handling(openai_wrapper):
    openai_wrapper.threads.delete = AsyncMock(side_effect=OpenAIRequestError(message="API error"))
    with pytest.raises(OpenAIRequestError):
        await openai_wrapper.delete_thread('thread-id')

# Include tests for messaging, runs, files, and tools functionality as well

# Example for context management
@pytest.mark.asyncio
async def test_wrapper_context_manager(mock_api_client):
    async with OpenAIWrapper(api_client=mock_api_client) as wrapper:
        assert wrapper is not None
    mock_api_client.__aenter__.assert_awaited_once()
    mock_api_client.__aexit__.assert_awaited_once()
