##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\utils.py

import logging
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Any, Dict, List
from .exceptions import OpenAIRequestError

# Set up structured logging
logger = logging.getLogger(__name__)

async def handle_http_error(response: aiohttp.ClientResponse) -> None:
    """Asynchronously handles HTTP errors by raising an OpenAIRequestError with detailed message."""
    if response.status >= 400:
        try:
            json_response = await response.json()
            error_message = json_response.get('error', {}).get('message', 'No error message provided.')
            error_type = json_response.get('error', {}).get('type', 'APIError')
            request_id = response.headers.get('X-Request-ID', 'N/A')
        except Exception:
            error_message = await response.text()
            error_type = 'UnknownError'
            request_id = 'N/A'
        
        raise OpenAIRequestError(message=error_message, status_code=response.status, error_type=error_type, request_id=request_id)

def log_api_call(method: str, url: str, status_code: int = None, duration: float = None, data: Dict[str, Any] = None) -> None:
    """Logs details of an API call including method, URL, status, duration, and data in a structured format."""
    log_data = {
        "event": "APIRequest",
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration": f"{duration:.2f}s",
        "data": data or {}
    }
    logger.info(json.dumps(log_data))

def validate_response_content_type(response: aiohttp.ClientResponse, expected_content_type: str) -> None:
    """Validates the Content-Type of the response asynchronously."""
    content_type = response.headers.get('Content-Type', '')
    if expected_content_type not in content_type:
        raise ValueError(f"Unexpected Content-Type: {content_type}, expected {expected_content_type}.")

def format_data_for_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Formats data to be sent in an API request."""
    return {k: v for k, v in data.items() if v is not None}

def validate_list_of_dicts(items: List[Dict[str, Any]], required_keys: List[str]) -> bool:
    """Validates that each dictionary in a list contains all required keys."""
    return all(all(key in item for key in required_keys) for item in items)

def datetime_to_iso(dt: datetime) -> str:
    """Converts a datetime object to an ISO formatted string."""
    return dt.isoformat()

def sanitize_input(input_string: str) -> str:
    """Sanitizes input strings to remove potentially harmful characters or patterns."""
    # Implement specific sanitization rules as needed
    return input_string.strip()

async def fetch_all_pages(fetch_page_function, **params) -> List[Dict[str, Any]]:
    """Utility function to fetch all pages of a paginated API response asynchronously."""
    all_items = []
    page_token = None

    while True:
        try:
            response, next_page_token = await fetch_page_function(page_token=page_token, **params)
        except OpenAIRequestError as e:
            logger.warning(f"Encountered an error: {e}. Retrying...")
            await asyncio.sleep(1)  # Simple backoff, adjust as needed
            continue  # Retry the current page fetch

        all_items.extend(response)
        if not next_page_token:
            break
        page_token = next_page_token

    return all_items
