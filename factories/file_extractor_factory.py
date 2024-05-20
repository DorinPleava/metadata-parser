from extractors.combox_extractor import ComboxExtractor
from extractors.gin_container_extractor import GinContainerExtractor
from extractors.speech_extractor import SpeechExtractor


class FileExtractorFactory:
    def __init__(self):
        self.extractors = {
            ComboxExtractor(): "COMBOX",
            SpeechExtractor(): "SPEECH",
            GinContainerExtractor(): "GIN",
        }

    def extract_metadata(self, file_path: str) -> dict:
        """Extract metadata from a file path.
        It will try to extract metadata using each of the available extractors.
        If an extractor finds a match, it will return the metadata extracted.

        Args:
            file_path (str): The path to the file.

        Returns:
            dict: A dictionary with the extracted metadata.
        """

        for extractor, file_type in self.extractors.items():
            match = extractor.extract(file_path)
            if match:
                return {"file_type": file_type, **match}
        return {}
