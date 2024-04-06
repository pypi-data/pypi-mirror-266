##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\threads.py

import logging
import asyncio  # Necessary for async operations

class ThreadManager:
    def __init__(self, api_client):
        """Initializes the ThreadManager with an API client."""
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    def _validate_thread_id(self, thread_id):
        """Validates that a thread ID is provided and not empty."""
        if not thread_id:
            raise ValueError("Thread ID must be provided and cannot be empty.")

    async def create(self, **kwargs):
        """Creates a new thread asynchronously."""
        self.logger.info("Creating new thread")
        # Ensure api_client.make_api_call is awaited and thus async
        return await self.api_client.make_api_call("threads", method="POST", data=kwargs)

    async def retrieve(self, thread_id):
        """Retrieves a specific thread by ID asynchronously."""
        self._validate_thread_id(thread_id)
        self.logger.info(f"Retrieving thread with ID: {thread_id}")
        return await self.api_client.make_api_call(f"threads/{thread_id}", method="GET")

    async def update(self, thread_id, **kwargs):
        """Updates a specific thread asynchronously."""
        self._validate_thread_id(thread_id)
        self.logger.info(f"Updating thread with ID: {thread_id}")
        return await self.api_client.make_api_call(f"threads/{thread_id}", method="PATCH", data=kwargs)

    async def delete(self, thread_id):
        """Deletes a specific thread by ID asynchronously."""
        self._validate_thread_id(thread_id)
        self.logger.info(f"Deleting thread with ID: {thread_id}")
        return await self.api_client.make_api_call(f"threads/{thread_id}", method="DELETE")

    async def list(self, **kwargs):
        """Lists all threads asynchronously, with optional filtering parameters."""
        self.logger.info("Listing all threads")
        return await self.api_client.make_api_call("threads", method="GET", params=kwargs)

    async def list_all_threads(self):
        """Utility method to fetch and return all threads, handling pagination automatically."""
        all_threads = []
        page_token = None
        is_first_page = True
        
        # Continue fetching pages until there are no more pages
        while is_first_page or page_token:
            params = {'after': page_token} if page_token else {}
            page = await self.list(**params)
            threads_data = page.get('data', [])
            all_threads.extend(threads_data)
            
            # Update variables for next iteration
            page_token = page.get('pagination', {}).get('next_page_token')
            is_first_page = False
            
        return all_threads

