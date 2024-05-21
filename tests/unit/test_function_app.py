import pytest
import json
import logging
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path
from urllib.parse import urlparse
import azure.functions as func
from function_app import send_message_to_eventhub, eventhub_trigger, process_event


@pytest.fixture
def mock_event():
    # Create a mock EventHubEvent
    mock_event = Mock(spec=func.EventHubEvent)
    mock_event.get_body.return_value = json.dumps(
        [{"data": {"url": "https://example.com/path/ComBoxApp_1234/filename.txt", "contentLength": 12345}}]
    ).encode('utf-8')
    return mock_event


@pytest.mark.asyncio
@patch('function_app.FileExtractorFactory')
@patch('function_app.FileProducer')
async def test_process_event(mock_file_producer, mock_file_extractor_factory, mock_event, caplog):
    # Setup mock for FileExtractorFactory
    mock_extractor = Mock()
    mock_extractor.extract_metadata.return_value = {"metadata_key": "metadata_value"}
    mock_file_extractor_factory.return_value = mock_extractor

    # Setup mock for FileProducer
    mock_producer = AsyncMock()
    mock_file_producer.return_value.get_producer.return_value.__aenter__.return_value = mock_producer

    with caplog.at_level(logging.INFO):
        await process_event(mock_event)

        assert "Storage to Hub event" in caplog.text
        assert "Metadata extracted" in caplog.text
        mock_producer.send_event.assert_called_once()

        # Verify the event data sent to the producer
        event_data_sent = mock_producer.send_event.call_args[0][0]
        event_data_dict = json.loads(event_data_sent.body_as_str())
        assert event_data_dict["filename"] == "filename.txt"
        assert event_data_dict["vehicle_vin"] == "ComBoxApp_1234"
        assert event_data_dict["size"] == 12345
        assert event_data_dict["metadata_key"] == "metadata_value"


@pytest.mark.asyncio
async def test_process_event_invalid_json(mock_event, caplog):
    # Modify the mock event to have invalid JSON
    mock_event.get_body.return_value = b'invalid json'

    with caplog.at_level(logging.ERROR):
        await process_event(mock_event)
        assert "Failed to parse JSON body from event" in caplog.text


@pytest.mark.asyncio
async def test_eprocess_event_no_combox(mock_event, caplog):
    # Modify the mock event to have a URL without ComBoxApp
    mock_event.get_body.return_value = json.dumps(
        [{"data": {"url": "https://example.com/path/filename.txt", "contentLength": 12345}}]
    ).encode('utf-8')

    with caplog.at_level(logging.ERROR):
        await process_event(mock_event)
        assert "Could not determine Combox" in caplog.text
