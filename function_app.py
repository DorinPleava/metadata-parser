import logging
import azure.functions as func


app = func.FunctionApp()


@app.event_hub_message_trigger(
    arg_name="azeventhub",
    event_hub_name="myeventhub",
    connection="eventhubnamespacemetadataparser_RootManageSharedAccessKey_EVENTHUB",
)
def eventhub_trigger(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s', azeventhub.get_body().decode('utf-8'))
