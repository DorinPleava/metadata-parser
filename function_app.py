import json
import logging
import azure.functions as func

from azure.eventhub import EventData

from event_producers.files_producer import FileProducer
from metadata_parser.event_extractor import EventExtractor


app = func.FunctionApp()


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="myeventhub",
    connection="pedshub_RootManageSharedAccessKey_storage_to_hub_event",
)
async def eventhub_trigger(azeventhub: func.EventHubEvent):
    await process_event(azeventhub)


async def process_event(azeventhub: func.EventHubEvent):
    logging.info(f"Storage to Hub event: {azeventhub.get_body().decode('utf-8')} triggered")
    extracted_metadata = EventExtractor(azeventhub).extract_metadata()

    logging.info("Metadata extracted")
    async with FileProducer().get_producer() as producer:
        event_data = EventData(json.dumps(extracted_metadata))
        await producer.send_event(event_data)

    logging.info(f"Sent message to metadata_parsed_event: {event_data}")


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="metadata_parsed_event",
    connection="pedshub_RootManageSharedAccessKey_metadata_parsed_event",
)
def metadata_parsed_event(azeventhub: func.EventHubEvent):
    logging.info(f"Received message from metadata_parsed_event: {azeventhub.get_body().decode('utf-8')}")
