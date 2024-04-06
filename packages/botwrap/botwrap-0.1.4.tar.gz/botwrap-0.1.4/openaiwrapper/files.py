##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\files.py

import os
import aiohttp
import logging
import asyncio
import functools
from .api_client import OpenAIAPIClient, OpenAIRequestError

class FileOperationError(Exception):
    """Custom exception for file operation errors."""
    pass

# Updated retry decorator for async functions
def retry(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        retries = 5
        base_delay = 0.5  # seconds
        factor = 2.0
        for i in range(retries):
            try:
                return await func(*args, **kwargs)
            except (aiohttp.ClientError, OpenAIRequestError) as e:
                if i < retries - 1:
                    sleep_time = base_delay * (factor ** i)
                    logging.warning(f"Retrying in {sleep_time:.2f}s... ({i+1}/{retries})")
                    await asyncio.sleep(sleep_time)
                else:
                    raise e
    return wrapper

class FileManager:
    def __init__(self, api_client: OpenAIAPIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    @retry
    async def upload_file(self, file_path: str):
        """Uploads a file to the OpenAI API asynchronously with retry logic."""
        self.validate_file_for_upload(file_path)
        url = f"{self.api_client.base_url}/files"
        headers = {"Authorization": f"Bearer {self.api_client.api_key}"}

        with open(file_path, "rb") as file_stream:
            files = {"file": (os.path.basename(file_path), file_stream)}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=files) as response:
                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientResponseError as e:
                self.logger.error(f"HTTPError during file upload: {e}")
                raise FileOperationError(f"HTTPError during file upload: {e.message}")
            except Exception as e:
                self.logger.error(f"Unexpected error during file upload: {e}")
                raise FileOperationError(f"Unexpected error during file upload: {e}")

    @retry
    async def delete_file(self, file_id: str):
        """Deletes a specific file by ID asynchronously with retry logic."""
        try:
            return await self.api_client.make_api_call(f"files/{file_id}", method="DELETE")
        except OpenAIRequestError as e:
            raise FileOperationError(f"Failed to delete file {file_id}: {e}")

    @retry
    async def get_file_content(self, file_id: str):
        """Fetches and returns the content of a specified file asynchronously with retry logic."""
        try:
            response = await self.api_client.make_api_call(f"files/{file_id}/content", method="GET", stream=True)
            return await response.read()
        except OpenAIRequestError as e:
            raise FileOperationError(f"Failed to fetch content for file {file_id}: {e}")

    @retry
    async def list_files(self, **kwargs):
        """Lists files with optional filtering and sorting asynchronously with retry logic."""
        params = {key: value for key, value in kwargs.items() if value is not None}
        try:
            response = await self.api_client.make_api_call("files", method="GET", params=params)
            return await response.json()
        except OpenAIRequestError as e:
            raise FileOperationError(f"Failed to list files: {e}")

    def validate_file_for_upload(self, file_path: str):
        """Validates the file against OpenAI's upload constraints before uploading.

        Args:
            file_path: Path to the file to be validated.

        Raises:
            ValueError: If the file does not meet the criteria for upload.
        """
        # This method remains synchronous as it doesn't perform I/O operations
        max_file_size = 52428800  # 50 MB for example
        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            raise ValueError("File exceeds the maximum allowed size.")
        # Additional validations can be added here.
