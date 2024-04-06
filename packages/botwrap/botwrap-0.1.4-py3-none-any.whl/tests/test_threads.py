##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\threads.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_threads.py

import pytest
from unittest.mock import AsyncMock
from openaiwrapper.threads import ThreadManager

@pytest.fixture
def mock_api_client():
    client = AsyncMock()
    return client

@pytest.fixture
def thread_manager(mock_api_client):
    return ThreadManager(api_client=mock_api_client)

@pytest.mark.asyncio
async def test_create_thread(thread_manager):
    thread_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'thread-id'})
    response = await thread_manager.create(name="Test Thread")
    assert response == {'id': 'thread-id'}
    thread_manager.api_client.make_api_call.assert_awaited_once_with("threads", method="POST", data={"name": "Test Thread"})

@pytest.mark.asyncio
async def test_retrieve_thread(thread_manager):
    thread_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'thread-id', 'name': 'Test Thread'})
    response = await thread_manager.retrieve(thread_id="thread-id")
    assert response == {'id': 'thread-id', 'name': 'Test Thread'}

@pytest.mark.asyncio
async def test_update_thread(thread_manager):
    thread_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'thread-id', 'name': 'Updated Test Thread'})
    response = await thread_manager.update(thread_id="thread-id", name="Updated Test Thread")
    assert response == {'id': 'thread-id', 'name': 'Updated Test Thread'}

@pytest.mark.asyncio
async def test_delete_thread(thread_manager):
    thread_manager.api_client.make_api_call = AsyncMock(return_value=True)
    response = await thread_manager.delete(thread_id="thread-id")
    assert response is True

@pytest.mark.asyncio
async def test_list_threads(thread_manager):
    thread_manager.api_client.make_api_call = AsyncMock(return_value={'data': [{'id': 'thread1'}, {'id': 'thread2'}], 'pagination': {}})
    threads = await thread_manager.list()
    assert len(threads['data']) == 2
    assert threads['data'][0]['id'] == 'thread1'
    assert threads['data'][1]['id'] == 'thread2'

@pytest.mark.asyncio
async def test_list_all_threads(thread_manager):
    # Simulate pagination by having two pages of threads
    thread_manager.api_client.make_api_call = AsyncMock(side_effect=[
        {'data': [{'id': 'thread1'}], 'pagination': {'next_page_token': 'next-token'}},
        {'data': [{'id': 'thread2'}], 'pagination': {}}
    ])
    all_threads = await thread_manager.list_all_threads()
    assert len(all_threads) == 2
    assert all_threads[0]['id'] == 'thread1'
    assert all_threads[1]['id'] == 'thread2'
    assert thread_manager.api_client.make_api_call.await_count == 2

# Add more tests as needed for comprehensive coverage
