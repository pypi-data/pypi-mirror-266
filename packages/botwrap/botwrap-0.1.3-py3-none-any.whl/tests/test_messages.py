##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\messages.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_messages.py

import pytest
from unittest.mock import AsyncMock
from openaiwrapper.messages import MessageManager
from openaiwrapper.exceptions import OpenAIRequestError

@pytest.fixture
def mock_api_client():
    client = AsyncMock()
    return client

@pytest.fixture
def message_manager(mock_api_client):
    return MessageManager(api_client=mock_api_client)

@pytest.mark.asyncio
async def test_create_message_valid(message_manager):
    message_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'message-id'})
    
    response = await message_manager.create(thread_id="thread-id", content="Hello, World!")
    assert response == {'id': 'message-id'}
    message_manager.api_client.make_api_call.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_message_empty_content(message_manager):
    with pytest.raises(ValueError):
        await message_manager.create(thread_id="thread-id", content=" ")

@pytest.mark.asyncio
async def test_create_message_invalid_role(message_manager):
    with pytest.raises(ValueError):
        await message_manager.create(thread_id="thread-id", content="Hello, World!", role="invalid")

@pytest.mark.asyncio
async def test_retrieve_message(message_manager):
    message_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'message-id', 'content': 'Hello, World!'})
    
    response = await message_manager.retrieve(thread_id="thread-id", message_id="message-id")
    assert response == {'id': 'message-id', 'content': 'Hello, World!'}

@pytest.mark.asyncio
async def test_delete_message(message_manager):
    message_manager.api_client.make_api_call = AsyncMock(return_value=True)
    
    response = await message_manager.delete(thread_id="thread-id", message_id="message-id")
    assert response is True

@pytest.mark.asyncio
async def test_list_messages(message_manager):
    message_manager.api_client.make_api_call = AsyncMock(return_value=[{'id': 'message1'}, {'id': 'message2'}])
    
    messages = await message_manager.list(thread_id="thread-id")
    assert len(messages) == 2
    assert messages[0]['id'] == 'message1'
    assert messages[1]['id'] == 'message2'

# Add more tests as needed for comprehensive coverage
