import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import azure.functions as func

# from peds.ava_interface import AvaClient

from extractors.combox_extractor import ComboxExtractor
from extractors.gin_container_extractor import GinContainerExtractor
from extractors.speech_extractor import SpeechExtractor


class EventExtractor:
    def __init__(self, azeventhub: func.EventHubEvent) -> None:
        self.extractors = {
            ComboxExtractor(): "COMBOX",
            SpeechExtractor(): "SPEECH",
            GinContainerExtractor(): "GIN",
        }
        self.azeventhub = azeventhub
        # self.ava_client = AvaClient("http://dewscap0013.emea.porsche.biz:6062/api/")

    def _extract_combox_from_path(self, path: str) -> str:
        """Extract the Combox account from the path.
        The Combox account is expected to be in the format ComBoxApp_ followed by a number.

        Args:
            path (str): The path to the file.

        Returns:
            str: The extracted Combox.
        """
        pattern = r"ComBoxApp_\d+"
        match = re.search(pattern, path)
        if match:
            return match.group(0)

        logging.error(f"Could not determine Combox from path: {path}")
        raise ValueError("Could not determine Combox")

    def _extract_metadata_from_body(self) -> dict:
        """Extract metadata from the body of the event."""
        try:
            event_body = json.loads(self.azeventhub.get_body().decode("utf-8"))
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON body from event")
            raise ValueError("Failed to parse JSON body from event")

        try:
            file_data = event_body[0]["data"]
            file_url = file_data["url"]
            content_length = file_data["contentLength"]
        except (IndexError, KeyError) as e:
            logging.error(f"Missing expected data in event body: {e}")
            raise ValueError(f"Missing expected data in event body: {e}")

        parsed_url = urlparse(file_url)
        combox_account = self._extract_combox_from_path(parsed_url.path)
        filename = Path(parsed_url.path).name

        return {"account": combox_account, "filename": filename, "size": content_length}

    def _extract_metadata_from_filename(self, filename: str) -> dict:
        """Extract metadata from a file path.
        It will try to extract metadata using each of the available extractors.
        If an extractor finds a match, it will return the metadata extracted.

        Args:
            file_path (str): The path to the file.

        Returns:
            dict: A dictionary with the extracted metadata.
        """

        for extractor, file_type in self.extractors.items():
            match = extractor.extract(filename)
            if match:
                return {"file_type": file_type, **match}
        return {}

    def extract_metadata(self) -> dict:
        """Extract metadata from the event."""
        body_metadata = self._extract_metadata_from_body()
        filename_metadata = self._extract_metadata_from_filename(body_metadata["filename"])

        if not filename_metadata:
            logging.error(f"Could not extract metadata from filename: {body_metadata['filename']}")
            raise ValueError(f"Could not extract metadata from filename: {body_metadata['filename']}")

        # fetch vehicle VIN from the file content

        # ava_vehicle = self.ava_client.get_vehicle_table_entry_by_account(body_metadata["account"])
        # if not ava_vehicle:
        #     self.logger.warning(f"Vehicle not found for account {body_metadata['account']}. Cannot extract vehicle VIN")
        #     raise ValueError(f"Vehicle not found for account {body_metadata['account']}")

        # vehicle_vin = ava_vehicle.vin
        vehicle_vin = "VIN1234"  # Placeholder for the VIN extraction

        return {**body_metadata, **filename_metadata, "vehicle_vin": vehicle_vin}
