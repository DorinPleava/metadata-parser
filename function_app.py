import logging
import azure.functions as func

# from azure.eventhub import EventData
# from azure.eventhub.aio import EventHubProducerClient
import asyncio


app = func.FunctionApp()


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="file_uploaded_trigger",
    connection="pedshub_RootManageSharedAccessKey_EVENTHUB",
)
def file_uploaded_trigger(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s', azeventhub.get_body().decode('utf-8'))
