##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\runs.py

import logging
import asyncio  # Use asyncio for async sleep instead of time.sleep

class RunManager:
    def __init__(self, api_client):
        """Initializes the RunManager with an async API client."""
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    async def create(self, thread_id, assistant_id, **kwargs):
        """Creates a Run for a Thread with the specified Assistant asynchronously."""
        data = {"assistant_id": assistant_id, **kwargs}
        try:
            response = await self.api_client.make_api_call(f"threads/{thread_id}/runs", method="POST", data=data)
            return response  # Assuming handle_api_response is handled within the api_client
        except Exception as e:
            self.logger.error(f"Failed to create run for thread {thread_id} with assistant {assistant_id}: {e}")
            raise

    async def retrieve(self, thread_id, run_id):
        """Asynchronously retrieves details of a specific Run."""
        try:
            return await self.api_client.make_api_call(f"threads/{thread_id}/runs/{run_id}", method="GET")
        except Exception as e:
            self.logger.error(f"Failed to retrieve run {run_id} from thread {thread_id}: {e}")
            raise

    async def wait_for_run_completion(self, thread_id, run_id, timeout=300):
        """Asynchronously waits for a run to complete and returns its status."""
        start_time = asyncio.get_event_loop().time()
        while True:
            run_status = await self.retrieve(thread_id, run_id)
            if run_status.get('status') == 'completed':
                self.logger.info("Run completed successfully.")
                return run_status
            elif run_status.get('status') == 'failed':
                self.logger.error("Run failed.")
                return run_status
            elif asyncio.get_event_loop().time() - start_time > timeout:
                self.logger.error("Run timed out.")
                return None
            await asyncio.sleep(10)  # Asynchronously wait before the next poll

    async def list(self, thread_id, **kwargs):
        """Asynchronously lists all runs for a specific thread, supporting pagination."""
        try:
            response = await self.api_client.make_api_call(f"threads/{thread_id}/runs", method="GET", params=kwargs)
            runs = response.get('data')
            next_page_token = response.get('pagination', {}).get('next_page_token')
            return runs, next_page_token
        except Exception as e:
            self.logger.error(f"Failed to list runs for thread {thread_id}: {e}")
            raise
