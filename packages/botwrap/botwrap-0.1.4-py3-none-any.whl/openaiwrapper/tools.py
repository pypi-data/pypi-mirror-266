##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\tools.py

import logging
from .exceptions import OpenAIRequestError  # Ensure this is correctly imported

class ToolsManager:
    def __init__(self, api_client):
        """Initializes the ToolsManager with an API client."""
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    async def update_tools(self, assistant_id, tools_config):
        """Updates the tools configuration for a specific Assistant asynchronously."""
        if not isinstance(tools_config, list) or not all(isinstance(tool, dict) for tool in tools_config):
            self.logger.error("tools_config must be a list of dictionaries.")
            raise ValueError("tools_config must be a list of dictionaries.")

        data = {"tools": tools_config}
        try:
            return await self.api_client.make_api_call(f"assistants/{assistant_id}/tools", method="PATCH", data=data)
        except OpenAIRequestError as e:
            self.logger.error(f"Failed to update tools for assistant {assistant_id}: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while updating tools for assistant {assistant_id}: {e}")
            raise

    async def retrieve_tool_configuration(self, assistant_id):
        """Retrieves the current tool configuration for a specific assistant asynchronously."""
        try:
            response = await self.api_client.make_api_call(f"assistants/{assistant_id}/tools", method="GET")
            return response.get('tools', [])
        except OpenAIRequestError as e:
            self.logger.error(f"Failed to retrieve tool configuration for assistant {assistant_id}: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while retrieving tool configuration for assistant {assistant_id}: {e}")
            raise

    async def remove_tool(self, assistant_id, tool_type):
        """Removes a specific tool based on tool type from an assistant's configuration asynchronously."""
        current_tools = await self.retrieve_tool_configuration(assistant_id)
        updated_tools = [tool for tool in current_tools if tool.get('type') != tool_type]

        return await self.update_tools(assistant_id, updated_tools)

    async def submit_tool_outputs(self, thread_id, run_id, tool_outputs):
        """Submits tool outputs for a specific run to continue processing asynchronously."""
        data = {"tool_outputs": tool_outputs}
        try:
            return await self.api_client.make_api_call(f"threads/{thread_id}/runs/{run_id}/submit_tool_outputs", method="POST", data=data)
        except OpenAIRequestError as e:
            self.logger.error(f"Failed to submit tool outputs for run {run_id} in thread {thread_id}: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while submitting tool outputs for run {run_id} in thread {thread_id}: {e}")
            raise

