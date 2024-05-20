import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse
import azure.functions as func

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

from event_producers.files_producer import FileProducer
from factories.file_extractor_factory import FileExtractorFactory

app = func.FunctionApp()


async def send_message_to_eventhub(event_data: EventData, event_hub_name: str, connection_string: str):
    producer = EventHubProducerClient.from_connection_string(conn_str=connection_string, eventhub_name=event_hub_name)

    async with producer:
        await producer.send_event(event_data)


# [
#     {
#         "topic": "/subscriptions/1b7eeb50-397d-4601-9d50-6ed3f4c002d6/resourceGroups/PEDS/providers/Microsoft.Storage/storageAccounts/pedsstorage",
#         "subject": "/blobServices/default/containers/peds/blobs/PEDS_OTA_ComBoxApp_110-2024-05-15-13-22-31/010_Recordings/Data1F2825.gz_20240514085305_1f8e13f289b652329c21367381db6a61",
#         "eventType": "Microsoft.Storage.BlobCreated",
#         "id": "e4014ba1-801e-0027-6735-a8f42e0622c4",
#         "data": {
#             "api": "PutBlob",
#             "clientRequestId": "403f2866-c8e6-48b1-6cf3-ec8809e5748d",
#             "requestId": "e4014ba1-801e-0027-6735-a8f42e000000",
#             "eTag": "0x8DC764C97B9A622",
#             "contentType": "text/plain",
#             "contentLength": 12,
#             "blobType": "BlockBlob",
#             "url": "https://pedsstorage.blob.core.windows.net/peds/PEDS_OTA_ComBoxApp_110-2024-05-15-13-22-31/010_Recordings/Data1F2825.gz_20240514085305_1f8e13f289b652329c21367381db6a61",
#             "sequencer": "00000000000000000000000000042C1A0000000000019471",
#             "storageDiagnostics": {"batchId": "609187ef-8006-0045-0035-a83609000000"},
#         },
#         "dataVersion": "",
#         "metadataVersion": "1",
#         "eventTime": "2024-05-17T08:37:31.4896169Z",
#     }
# ]


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="myeventhub",
    connection="pedshub_RootManageSharedAccessKey_storage_to_hub_event",
)
async def eventhub_trigger(azeventhub: func.EventHubEvent):
    logging.info(f"Storage to Hub event: {azeventhub.get_body().decode('utf-8')} triggered")

    body_str = azeventhub.get_body().decode('utf-8')
    try:
        body_dict = json.loads(body_str)
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON body from event")
        return

    file_data = body_dict[0]["data"]
    complete_url = urlparse(file_data.get("url", ""))
    filename = Path(complete_url.path).name
    size = file_data.get("contentLength", 0)

    extracted_metadata = FileExtractorFactory().extract_metadata(filename)

    if extracted_metadata:
        logging.info(f"Metadata extracted: {extracted_metadata}")
    else:
        logging.info(f"Cound not extract metadata from {filename}, returning only filename and size")

    async with FileProducer().get_producer() as producer:
        event_data = EventData(json.dumps({"filename": filename, "size": size, **extracted_metadata}))
        await producer.send_event(event_data)

    logging.info(f"Sent message to metadata_parsed_event: {event_data}")


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="metadata_parsed_event",
    connection="pedshub_RootManageSharedAccessKey_metadata_parsed_event",
)
def metadata_parsed_event(azeventhub: func.EventHubEvent):
    logging.info(f"Received message from metadata_parsed_event: {azeventhub.get_body().decode('utf-8')}")
