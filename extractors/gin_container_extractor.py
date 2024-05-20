import re
from extractors.metadata_extractor import MetadataExtractor


class GinContainerExtractor(MetadataExtractor):
    def extract(self, file_path: str) -> dict:
        pattern = re.compile(r".*gin_container_(?P<trigger_file_hash>\w+).zip")
        match = pattern.search(file_path)
        if match:
            return match.groupdict()
        return {}
