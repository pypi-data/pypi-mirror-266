##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\runs.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_runs.py

import pytest
from unittest.mock import AsyncMock
from openaiwrapper.runs import RunManager

@pytest.fixture
def mock_api_client():
    client = AsyncMock()
    return client

@pytest.fixture
def run_manager(mock_api_client):
    return RunManager(api_client=mock_api_client)

@pytest.mark.asyncio
async def test_create_run(run_manager):
    run_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'run-id'})
    response = await run_manager.create(thread_id="thread-id", assistant_id="assistant-id")
    assert response == {'id': 'run-id'}
    run_manager.api_client.make_api_call.assert_awaited_once_with(
        "threads/thread-id/runs", method="POST", data={"assistant_id": "assistant-id"}
    )

@pytest.mark.asyncio
async def test_retrieve_run(run_manager):
    run_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'run-id', 'status': 'completed'})
    response = await run_manager.retrieve(thread_id="thread-id", run_id="run-id")
    assert response == {'id': 'run-id', 'status': 'completed'}

@pytest.mark.asyncio
async def test_wait_for_run_completion_completed(run_manager):
    run_manager.retrieve = AsyncMock(side_effect=[
        {'status': 'in_progress'}, {'status': 'in_progress'}, {'status': 'completed'}
    ])
    response = await run_manager.wait_for_run_completion(thread_id="thread-id", run_id="run-id")
    assert response == {'status': 'completed'}
    assert run_manager.retrieve.await_count == 3

@pytest.mark.asyncio
async def test_wait_for_run_completion_timeout(run_manager):
    run_manager.retrieve = AsyncMock(return_value={'status': 'in_progress'})
    response = await run_manager.wait_for_run_completion(thread_id="thread-id", run_id="run-id", timeout=1)
    assert response is None

@pytest.mark.asyncio
async def test_list_runs(run_manager):
    run_manager.api_client.make_api_call = AsyncMock(return_value={
        'data': [{'id': 'run1'}, {'id': 'run2'}], 'pagination': {'next_page_token': 'token123'}
    })
    runs, next_page_token = await run_manager.list(thread_id="thread-id")
    assert len(runs) == 2
    assert runs[0]['id'] == 'run1'
    assert next_page_token == 'token123'

# Add more tests as needed for comprehensive coverage
