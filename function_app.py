import logging
import os
import azure.functions as func

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
import asyncio

app = func.FunctionApp()


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="myeventhub",
    connection="pedshub_RootManageSharedAccessKey_storage-to-hub-event",
)
async def eventhub_trigger(azeventhub: func.EventHubEvent):
    logging.info(f"Storage to Hub event: {azeventhub.get_body().decode('utf-8')} triggered")

    # do the metadata parsing here

    # Send the parsed metadata to the target Event Hub

    # The connection string for the target Event Hub
    TARGET_EVENT_HUB_CONNECTION_STR = os.environ["pedshub_RootManageSharedAccessKey_metadata-parsed-event"]

    # The name of the target Event Hub
    METADATA_PARSED_EVENT_HUB_NAME = os.environ["metadata_parsed_event_hub_name"] or "metadata-parsed-event"

    # Create an Event Hub producer client
    producer = EventHubProducerClient.from_connection_string(
        conn_str=TARGET_EVENT_HUB_CONNECTION_STR, eventhub_name=METADATA_PARSED_EVENT_HUB_NAME
    )

    # Send a message to the target Event Hub
    async with producer:
        event_data = EventData("This is a message from the metadata_parsed_event function")
        await producer.send_event(event_data)

    # return "Message sent to target Event Hub"


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="metadata_parsed_event",
    connection="pedshub_RootManageSharedAccessKey_metadata-parsed-event",
)
def metadata_parsed_event(azeventhub: func.EventHubEvent):
    logging.info(f"Received message from metadata_parsed_event: {azeventhub.get_body().decode('utf-8')}")
