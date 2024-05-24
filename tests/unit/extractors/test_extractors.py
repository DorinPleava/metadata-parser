import json
from unittest.mock import Mock, patch
import pytest

from factories.event_extractor import EventExtractor
from tests.unit.fixtures.regex_fixtures import (
    combox_file_path_test_cases,
    gin_container_file_path_test_cases,
    speech_file_path_test_cases,
)

import azure.functions as func


@pytest.mark.parametrize("file_path,expected_output", combox_file_path_test_cases)
def test_extract_metadata_from_combox_filename(file_path, expected_output):

    extracted_metadata = EventExtractor(None)._extract_metadata_from_filename(file_path)

    assert extracted_metadata == expected_output


@pytest.mark.parametrize("file_path,expected_output", gin_container_file_path_test_cases)
def test_extract_metadata_from_gin_container_filename(file_path, expected_output):
    extracted_metadata = EventExtractor(None)._extract_metadata_from_filename(file_path)

    assert extracted_metadata == expected_output


@pytest.mark.parametrize("file_path,expected_output", speech_file_path_test_cases)
def test_extract_metadata_from_speech_filename(file_path, expected_output):
    extracted_metadata = EventExtractor(None)._extract_metadata_from_filename(file_path)

    assert extracted_metadata == expected_output


def test_extract_metadata_from_filename_invalid():
    extracted_metadata = EventExtractor(None)._extract_metadata_from_filename("invalid_filename")

    assert extracted_metadata == {}


def test_extract_metadata_from_filename_no_match():
    extracted_metadata = EventExtractor(None)._extract_metadata_from_filename("no_match_filename")

    assert extracted_metadata == {}


@pytest.fixture
def mock_event():
    # Create a mock EventHubEvent
    mock_event = Mock(spec=func.EventHubEvent)
    mock_event.get_body.return_value = json.dumps(
        [{"data": {"url": "https://example.com/path/ComBoxApp_1234/filename.txt", "contentLength": 12345}}]
    ).encode('utf-8')
    return mock_event


def test_extract_metadata_from_body(mock_event):
    extracted_metadata = EventExtractor(mock_event)._extract_metadata_from_body()

    assert extracted_metadata == {"account": "ComBoxApp_1234", "filename": "filename.txt", "size": 12345}


@pytest.fixture
def mock_real_event():
    # Create a mock EventHubEvent
    mock_event = Mock(spec=func.EventHubEvent)
    mock_event.get_body.return_value = json.dumps(
        [
            {
                "topic": "/subscriptions/1b7eeb50-397d-4601-9d50-6ed3f4c002d6/resourceGroups/PEDS/providers/Microsoft.Storage/storageAccounts/pedsstorage",
                "subject": "/blobServices/default/containers/peds/blobs/PEDS_OTA_ComBoxApp_110-2024-05-15-13-22-31/010_Recordings/Data1F2825.gz_20240514085305_1f8e13f289b652329c21367381db6a61",
                "eventType": "Microsoft.Storage.BlobCreated",
                "id": "e4014ba1-801e-0027-6735-a8f42e0622c4",
                "data": {
                    "api": "PutBlob",
                    "clientRequestId": "403f2866-c8e6-48b1-6cf3-ec8809e5748d",
                    "requestId": "e4014ba1-801e-0027-6735-a8f42e000000",
                    "eTag": "0x8DC764C97B9A622",
                    "contentType": "text/plain",
                    "contentLength": 12,
                    "blobType": "BlockBlob",
                    "url": "https://pedsstorage.blob.core.windows.net/peds/PEDS_OTA_ComBoxApp_110-2024-05-15-13-22-31/010_Recordings/Data1F2825.gz_20240514085305_1f8e13f289b652329c21367381db6a61",
                    "sequencer": "00000000000000000000000000042C1A0000000000019471",
                    "storageDiagnostics": {"batchId": "609187ef-8006-0045-0035-a83609000000"},
                },
                "dataVersion": "",
                "metadataVersion": "1",
                "eventTime": "2024-05-17T08:37:31.4896169Z",
            }
        ]
    ).encode('utf-8')
    return mock_event


@pytest.fixture
def mock_ava_call():
    with patch("peds.ava_interface.AvaClient.get_vehicle_table_entry_by_account") as mock_ava_call:
        # should return an object whos .vin is VIN1234
        mock_ava_call.return_value = Mock(vin="VIN1234")
        yield mock_ava_call


def test_extract_metadata_from_real_event(mock_real_event, mock_ava_call):
    extracted_metadata = EventExtractor(mock_real_event).extract_metadata()

    assert mock_ava_call.called

    assert extracted_metadata == {
        "account": "ComBoxApp_110",
        "filename": "Data1F2825.gz_20240514085305_1f8e13f289b652329c21367381db6a61",
        "size": 12,
        "file_type": "COMBOX",
        "vehicle_vin": "VIN1234",
        "timestamp": "20240514085305",
        "trigger_file_hash": "1f8e13f289b652329c21367381db6a61",
        "trigger_number": "2825",
    }
