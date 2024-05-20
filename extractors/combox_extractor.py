import re

from extractors.metadata_extractor import MetadataExtractor


class ComboxExtractor(MetadataExtractor):
    def extract(self, file_path: str) -> dict:
        pattern = re.compile(
            r".*(ml_rt.*|UserData\.Zip|Data[12]F)(?P<trigger_number>\d+)?(?:\.gz)?_(?P<timestamp>\d{14}?)(?:_(?P<trigger_file_hash>\w+))?"
        )
        match = pattern.search(file_path)
        if match:
            return match.groupdict()
        return {}
