##Path of module being tested C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\files.py
##Path of test C:\Users\jamig\OneDrive\Desktop\botwrap\tests\test_files.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from openaiwrapper.files import FileManager, FileOperationError

@pytest.fixture
def mock_api_client():
    client = AsyncMock()
    return client

@pytest.fixture
def file_manager(mock_api_client):
    return FileManager(api_client=mock_api_client)

@pytest.mark.asyncio
async def test_upload_file_valid(file_manager, mocker):
    mocker.patch("openaiwrapper.files.open", mocker.mock_open(read_data=b"file content"), create=True)
    mocker.patch("os.path.getsize", return_value=10)
    file_manager.api_client.make_api_call = AsyncMock(return_value={'id': 'file-id'})

    response = await file_manager.upload_file("path/to/file.txt")
    assert response == {'id': 'file-id'}

@pytest.mark.asyncio
async def test_delete_file_valid(file_manager):
    file_manager.api_client.make_api_call = AsyncMock(return_value=True)
    
    response = await file_manager.delete_file("file-id")
    assert response is True

@pytest.mark.asyncio
async def test_get_file_content_valid(file_manager):
    file_manager.api_client.make_api_call = AsyncMock(return_value=b"file content")
    
    content = await file_manager.get_file_content("file-id")
    assert content == b"file content"

@pytest.mark.asyncio
async def test_list_files_valid(file_manager):
    file_manager.api_client.make_api_call = AsyncMock(return_value=[{'id': 'file1'}, {'id': 'file2'}])
    
    files = await file_manager.list_files()
    assert len(files) == 2
    assert files[0]['id'] == 'file1'
    assert files[1]['id'] == 'file2'

def test_validate_file_for_upload_invalid(file_manager, mocker):
    mocker.patch("os.path.getsize", return_value=100000000)  # 100 MB
    
    with pytest.raises(ValueError):
        file_manager.validate_file_for_upload("path/to/largefile.txt")

# Add more tests for retry logic, error handling, etc.
