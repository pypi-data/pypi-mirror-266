import logging
import aiohttp

logger = logging.getLogger(__name__)

class OpenAIRequestError(Exception):
    """Custom exception for handling OpenAI API request errors."""
    def __init__(self, message=None, status_code=None, error_type=None, request_id=None):
        self.message = message or "An error occurred with the OpenAI API request."
        self.status_code = status_code
        self.error_type = error_type
        self.request_id = request_id  # Useful for logging and support
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.error_type or 'Error'}: {self.message} (Status code: {self.status_code}) Request ID: {self.request_id or 'N/A'}"

async def create_openai_request_error(response: aiohttp.ClientResponse):
    """Utility function to create an OpenAIRequestError from an aiohttp HTTP response."""
    try:
        error_details = await response.json()
        error_message = error_details.get('error', {}).get('message', 'No error message provided.')
        error_type = error_details.get('error', {}).get('type', 'Unknown')
    except aiohttp.ContentTypeError:
        text = await response.text()
        error_message = text or "Failed to decode JSON response."
        error_type = 'ContentTypeError'

    status_code = response.status
    request_id = response.headers.get('X-Request-ID')

    return OpenAIRequestError(message=error_message, status_code=status_code, error_type=error_type, request_id=request_id)

def log_openai_request_error(error: OpenAIRequestError):
    """Logs detailed information from an OpenAIRequestError."""
    logger.error(f"OpenAIRequestError encountered: {error.error_type or 'Error'} - {error.message} "
                 f"(Status code: {error.status_code}, Request ID: {error.request_id or 'N/A'})")
