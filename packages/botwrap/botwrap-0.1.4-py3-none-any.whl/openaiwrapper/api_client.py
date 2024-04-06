##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\api_client.py

import aiohttp
import logging
from aiohttp import ClientResponseError, ClientSession
from asyncio import sleep
from functools import wraps
from .exceptions import OpenAIRequestError  # Ensure this is correctly imported from your package structure

# Define constants for readability and configuration
DEFAULT_RETRY_ATTEMPTS = 3
CONTENT_TYPE_JSON = 'application/json'
API_BASE_URL = "https://api.openai.com/v1"  # This could also be configurable via an environment variable

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def retry(exceptions, tries=DEFAULT_RETRY_ATTEMPTS, delay=1, backoff=2, jitter=0.1):
    """A decorator for retrying a function with exponential backoff and jitter."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 0:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    if _tries == 0:
                        logger.error(f'Final attempt of {func.__name__} failed due to {e}, no more retries left.')
                        raise
                    wait = _delay + jitter * _delay * (random.random() - 0.5)  # Adding jitter
                    logger.warning(f'Retrying {func.__name__} due to {e}, attempt {tries - _tries} of {tries}. Waiting {wait} seconds.')
                    await sleep(wait)
                    _delay *= backoff
        return wrapper
    return decorator

class OpenAIAPIClient:
    def __init__(self, api_key: str, base_url=API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None  # Lazy instantiation of ClientSession

    async def __aenter__(self):
        if not self.session:  # Check if session has already been created
            self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    @retry(exceptions=(ClientResponseError,))
    async def _make_request(self, method: str, url: str, data=None, files=None, params=None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if not files:
            headers["Content-Type"] = CONTENT_TYPE_JSON
        
        # Ensure self.session is initialized before making a request
        if not self.session:
            self.session = ClientSession()

        full_url = f"{self.base_url}/{url}"
        async with self.session.request(method, full_url, headers=headers, json=data, params=params) as response:
            if response.status == 429:  # Rate limit handling
                retry_after = int(response.headers.get("Retry-After", "60"))
                logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                await sleep(retry_after)
                return await self._make_request(method, url, data, files, params)  # Recursive retry after delay
            response.raise_for_status()  # Raises error for 400 and 500 codes
            return await response.json()  # Assuming all successful responses are JSON

    async def make_api_call(self, endpoint: str, method: str = "GET", data=None, files=None, params=None) -> dict:
        return await self._make_request(method, endpoint, data=data, files=files, params=params)
