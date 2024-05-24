import pytest
import json
import logging
from unittest.mock import AsyncMock, Mock, patch
import azure.functions as func
from function_app import process_event


@pytest.fixture
def mock_event():
    # Create a mock EventHubEvent
    mock_event = Mock(spec=func.EventHubEvent)
    mock_event.get_body.return_value = json.dumps(
        [{"data": {"url": "https://example.com/path/ComBoxApp_1234/filename.txt", "contentLength": 12345}}]
    ).encode('utf-8')
    return mock_event


@pytest.mark.asyncio
@patch('function_app.EventExtractor')
@patch('function_app.FileProducer')
async def test_process_event_flow(mock_file_producer, mock_file_extractor_factory, mock_event, caplog):
    # Setup mock for EventExtractor
    mock_extractor = mock_file_extractor_factory.return_value
    mock_extractor.extract_metadata.return_value = {
        "account": "ComBoxApp_1234",
        "filename": "filename.txt",
        "size": 12345,
    }

    # Setup mock for FileProducer
    mock_producer = mock_file_producer.return_value
    mock_producer.get_producer.return_value.__aenter__.return_value = AsyncMock()
    mock_producer.get_producer.return_value.__aexit__.return_value = AsyncMock()

    await process_event(mock_event)

    assert mock_extractor.extract_metadata.called
    assert mock_producer.get_producer.called


@pytest.mark.asyncio
async def test_process_event_invalid_json(mock_event, caplog):
    # Modify the mock event to have invalid JSON
    mock_event.get_body.return_value = b'invalid json'

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            await process_event(mock_event)

        assert "Failed to parse JSON body from event" in caplog.text


@pytest.mark.asyncio
async def test_eprocess_event_no_combox(mock_event, caplog):
    # Modify the mock event to have a URL without ComBoxApp
    mock_event.get_body.return_value = json.dumps(
        [{"data": {"url": "https://example.com/path/filename.txt", "contentLength": 12345}}]
    ).encode('utf-8')

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            await process_event(mock_event)

        assert "Could not determine Combox from path" in caplog.text
