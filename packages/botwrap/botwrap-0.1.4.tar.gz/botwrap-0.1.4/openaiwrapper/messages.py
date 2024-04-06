##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\messages.py

import logging
from .exceptions import OpenAIRequestError  # Adjust import path as necessary

class MessageManager:
    def __init__(self, api_client):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    async def create(self, thread_id, content, role="user", **kwargs):
        """Sends a new message to a thread, validating inputs before sending."""
        if not content.strip():
            self.logger.error("Message content cannot be empty.")
            raise ValueError("Message content cannot be empty.")
        if role not in ["user", "assistant"]:
            self.logger.error("Role must be either 'user' or 'assistant'.")
            raise ValueError("Role must be either 'user' or 'assistant'.")

        data = {"content": content, "role": role, **kwargs}
        try:
            return await self.api_client.make_api_call(f"threads/{thread_id}/messages", method="POST", data=data)
        except OpenAIRequestError as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while creating a message in thread {thread_id}: {e}")
            raise

    async def retrieve(self, thread_id, message_id):
        """Retrieves a specific message by ID from a thread asynchronously."""
        try:
            return await self.api_client.make_api_call(f"threads/{thread_id}/messages/{message_id}", method="GET")
        except OpenAIRequestError as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while retrieving message {message_id} from thread {thread_id}: {e}")
            raise

    async def delete(self, thread_id, message_id):
        """Deletes a specific message by ID from a thread asynchronously."""
        try:
            return await self.api_client.make_api_call(f"threads/{thread_id}/messages/{message_id}", method="DELETE")
        except OpenAIRequestError as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while deleting message {message_id} from thread {thread_id}: {e}")
            raise

    async def list(self, thread_id, **kwargs):
        """Lists all messages in a specific thread, supporting pagination, asynchronously."""
        try:
            return await self.api_client.make_api_call(f"threads/{thread_id}/messages", method="GET", params=kwargs)
        except OpenAIRequestError as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while listing messages in thread {thread_id}: {e}")
            raise
