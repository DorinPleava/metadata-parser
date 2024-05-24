import os
from event_producers.base_producer import BaseProducer
from azure.eventhub.aio import EventHubProducerClient


# in case we will add multiple producers
class FileProducer(BaseProducer):

    def __init__(self):
        self.producer = EventHubProducerClient.from_connection_string(
            conn_str=os.environ["pedshub_RootManageSharedAccessKey_metadata_parsed_event"],
            eventhub_name=os.environ["metadata_parsed_event_hub_name"] or "metadata-parsed-event",
        )

    def get_producer(self):
        return self.producer
