##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\openai_wrapper.py

import logging
from .exceptions import OpenAIRequestError

# Assuming these constants are defined elsewhere
API_KEY = 'your-api-key'
BASE_URL = 'https://api.openai.com'

# Logger setup
logger = logging.getLogger(__name__)

# Assuming OpenAIAPIClient and managers have been defined elsewhere
from your_package import (
    OpenAIAPIClient,
    AssistantManager,
    ThreadManager,
    MessageManager,
    RunManager,
    FileManager,
    ToolsManager
)

# from your_package.retry_decorator import retry  # If a retry decorator is available

class OpenAIWrapper:
    def __init__(self, api_key=API_KEY, base_url=BASE_URL):
        self.client = OpenAIAPIClient(api_key)
        self.client.base_url = base_url
        self.assistants = AssistantManager(self.client)
        self.threads = ThreadManager(self.client)
        self.messages = MessageManager(self.client)
        self.runs = RunManager(self.client)
        self.files = FileManager(self.client)
        self.tools = ToolsManager(self.client)

    def handle_error(self, e):
        if isinstance(e, OpenAIRequestError):
            logger.error(f"OpenAI API request failed: {e}")
        else:
            logger.exception("Unexpected error occurred")

    async def create_assistant(self, **kwargs):
        logger.debug(f"Creating assistant with parameters: {kwargs}")
        try:
            response = await self.assistants.create(**kwargs)
            logger.debug(f"Assistant created: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    @retry(exceptions=(OpenAIRequestError,), tries=3, delay=2)
    async def send_message(self, thread_id, content, role="user", **kwargs):
        logger.debug(f"Sending message to thread {thread_id} with content: {content}")
        try:
            response = await self.messages.create(thread_id, content, role, **kwargs)
            logger.debug(f"Message sent: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def cleanup_assistant_resources(self, assistant_id):
        logger.debug(f"Cleaning up resources for assistant {assistant_id}")
        try:
            await self.delete_assistant(assistant_id)
        except Exception as e:
            self.handle_error(e)

    async def update_assistant(self, assistant_id, **kwargs):
        logger.debug(f"Updating assistant {assistant_id} with parameters: {kwargs}")
        try:
            response = await self.assistants.update(assistant_id, **kwargs)
            logger.debug(f"Assistant updated: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def delete_assistant(self, assistant_id):
        logger.debug(f"Deleting assistant {assistant_id}")
        try:
            response = await self.assistants.delete(assistant_id)
            logger.debug(f"Assistant deleted: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def list_assistants(self, **kwargs):
        logger.debug("Listing assistants")
        try:
            response = await self.assistants.list(**kwargs)
            logger.debug("Assistants listed")
            return response
        except Exception as e:
            self.handle_error(e)

    async def create_thread(self):
        logger.debug("Creating new thread")
        try:
            response = await self.threads.create()
            logger.debug(f"Thread created: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def delete_thread(self, thread_id):
        logger.debug(f"Deleting thread {thread_id}")
        try:
            response = await self.threads.delete(thread_id)
            logger.debug(f"Thread deleted: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def list_threads(self, **kwargs):
        logger.debug("Listing threads")
        try:
            response = await self.threads.list(**kwargs)
            logger.debug("Threads listed")
            return response
        except Exception as e:
            self.handle_error(e)

    async def delete_message(self, thread_id, message_id):
        logger.debug(f"Deleting message {message_id} from thread {thread_id}")
        try:
            response = await self.messages.delete(thread_id, message_id)
            logger.debug(f"Message deleted: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def create_run(self, thread_id, assistant_id, **kwargs):
        logger.debug(f"Creating run for thread {thread_id} with assistant {assistant_id}")
        try:
            response = await self.runs.create(thread_id, assistant_id, **kwargs)
            logger.debug(f"Run created: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def upload_file(self, file_path, purpose="answers"):
        logger.debug(f"Uploading file {file_path} with purpose {purpose}")
        try:
            with open(file_path, 'rb') as file:
                response = await self.files.upload(file=file, purpose=purpose)
            logger.debug(f"File uploaded: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def delete_file(self, file_id):
        logger.debug(f"Deleting file {file_id}")
        try:
            response = await self.files.delete(file_id=file_id)
            logger.debug(f"File deleted: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

    async def update_tool_configuration(self, assistant_id, tools_config):
        logger.debug(f"Updating tool configuration for assistant {assistant_id}")
        try:
            response = await self.tools.update_tools(assistant_id, tools_config)
            logger.debug(f"Tool configuration updated: {response}")
            return response
        except Exception as e:
            self.handle_error(e)

# Add any other methods here as needed to interact with the OpenAI API.

##Proposed changes
import logging
from .exceptions import OpenAIRequestError  # Adjust import paths as necessary

# Logger setup
logger = logging.getLogger(__name__)

class OpenAIWrapper:
    def __init__(self, api_client):
        # Initialize with an instance of OpenAIAPIClient
        self.api_client = api_client
        # Assuming Manager classes are also updated to be async-compatible
        self.assistants = AssistantManager(self.api_client)
        self.threads = ThreadManager(self.api_client)
        self.messages = MessageManager(self.api_client)
        self.runs = RunManager(self.api_client)
        self.files = FileManager(self.api_client)
        self.tools = ToolsManager(self.api_client)

    async def create_assistant(self, **kwargs):
        """Asynchronously creates a new assistant."""
        try:
            response = await self.assistants.create(**kwargs)
            logger.info(f"Assistant created successfully: {response}")
            return response
        except OpenAIRequestError as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while creating an assistant: {e}")
            raise

    async def delete_assistant(self, assistant_id):
        """Asynchronously deletes an assistant."""
        try:
            response = await self.assistants.delete(assistant_id)
            logger.info(f"Assistant {assistant_id} deleted successfully.")
            return response
        except OpenAIRequestError as e:
            logger.error(f"Failed to delete assistant {assistant_id}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while deleting assistant {assistant_id}: {e}")
            raise

    async def list_assistants(self):
        """Asynchronously lists all assistants."""
        try:
            response = await self.assistants.list()
            logger.info("Assistants listed successfully.")
            return response
        except OpenAIRequestError as e:
            logger.error(f"Failed to list assistants: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error occurred while listing assistants.")
            raise

    async def update_assistant(self, assistant_id, **kwargs):
        """Asynchronously updates an assistant."""
        try:
            response = await self.assistants.update(assistant_id, **kwargs)
            logger.info(f"Assistant {assistant_id} updated successfully.")
            return response
        except OpenAIRequestError as e:
            logger.error(f"Failed to update assistant {assistant_id}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while updating assistant {assistant_id}: {e}")
            raise

    async def create_thread(self, **kwargs):
        """Asynchronously creates a new thread."""
        try:
            response = await self.threads.create(**kwargs)
            logger.info("Thread created successfully.")
            return response
        except OpenAIRequestError as e:
            logger.error("Failed to create thread.")
            raise
        except Exception as e:
            logger.exception("Unexpected error occurred while creating thread.")
            raise

    async def delete_thread(self, thread_id):
        """Asynchronously deletes a thread."""
        try:
            response = await self.threads.delete(thread_id)
            logger.info(f"Thread {thread_id} deleted successfully.")
            return response
        except OpenAIRequestError as e:
            logger.error(f"Failed to delete thread {thread_id}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while deleting thread {thread_id}.")
            raise

    async def list_threads(self, **kwargs):
        """Asynchronously lists all threads."""
        try:
            response = await self.threads.list(**kwargs)
            logger.info("Threads listed successfully.")
            return response
        except OpenAIRequestError as e:
            logger.error("Failed to list threads.")
            raise
        except Exception as e:
            logger.exception("Unexpected error occurred while listing threads.")
            raise

    # Make sure to include async context management if the OpenAIAPIClient uses it
    async def __aenter__(self):
        await self.api_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.api_client.__aexit__(exc_type, exc, tb)

