##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\tools.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_tools.py

import pytest
from unittest.mock import AsyncMock
from openaiwrapper.tools import ToolsManager
from openaiwrapper.exceptions import OpenAIRequestError

@pytest.fixture
def mock_api_client():
    client = AsyncMock()
    return client

@pytest.fixture
def tools_manager(mock_api_client):
    return ToolsManager(api_client=mock_api_client)

@pytest.mark.asyncio
async def test_update_tools_valid(tools_manager):
    valid_tools_config = [{"type": "code_interpreter"}]
    tools_manager.api_client.make_api_call = AsyncMock(return_value={'tools': valid_tools_config})
    response = await tools_manager.update_tools(assistant_id="assistant-id", tools_config=valid_tools_config)
    assert response == {'tools': valid_tools_config}
    tools_manager.api_client.make_api_call.assert_awaited_once_with(
        "assistants/assistant-id/tools", method="PATCH", data={"tools": valid_tools_config}
    )

@pytest.mark.asyncio
async def test_update_tools_invalid_config(tools_manager):
    invalid_tools_config = "invalid_config"
    with pytest.raises(ValueError):
        await tools_manager.update_tools(assistant_id="assistant-id", tools_config=invalid_tools_config)

@pytest.mark.asyncio
async def test_retrieve_tool_configuration(tools_manager):
    tools_manager.api_client.make_api_call = AsyncMock(return_value={'tools': [{"type": "code_interpreter"}]})
    response = await tools_manager.retrieve_tool_configuration(assistant_id="assistant-id")
    assert response == [{"type": "code_interpreter"}]

@pytest.mark.asyncio
async def test_remove_tool(tools_manager):
    current_tools = [{"type": "code_interpreter"}, {"type": "tool_to_remove"}]
    tools_manager.retrieve_tool_configuration = AsyncMock(return_value=current_tools)
    tools_manager.api_client.make_api_call = AsyncMock(return_value={'tools': [{"type": "code_interpreter"}]})
    response = await tools_manager.remove_tool(assistant_id="assistant-id", tool_type="tool_to_remove")
    assert response == {'tools': [{"type": "code_interpreter"}]}
    tools_manager.api_client.make_api_call.assert_awaited_once_with(
        "assistants/assistant-id/tools", method="PATCH", data={"tools": [{"type": "code_interpreter"}]}
    )

@pytest.mark.asyncio
async def test_submit_tool_outputs(tools_manager):
    tool_outputs = [{"tool_name": "code_interpreter", "output": "result"}]
    tools_manager.api_client.make_api_call = AsyncMock(return_value={'success': True})
    response = await tools_manager.submit_tool_outputs(thread_id="thread-id", run_id="run-id", tool_outputs=tool_outputs)
    assert response == {'success': True}

# Add more tests as needed for comprehensive coverage
