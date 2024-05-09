import logging
import azure.functions as func


app = func.FunctionApp()


@app.blob_trigger(arg_name="myblob", path="mycontainer", connection="pedsstorage_STORAGE")
def BlobTrigger(myblob: func.InputStream):
    logging.info(
        f"Python blob trigger function processed blob" f"Name: {myblob.name}" f"Blob Size: {myblob.length} bytes"
    )


@app.event_grid_trigger(arg_name="azeventgrid")
def EventGridTrigger(azeventgrid: func.EventGridEvent):
    logging.info(f"Python EventGrid trigger function processed event" f"Subject: {azeventgrid.subject}")
