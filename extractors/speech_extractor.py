import re
from extractors.metadata_extractor import MetadataExtractor


class SpeechExtractor(MetadataExtractor):
    def extract(self, file_path: str) -> dict:
        pattern = re.compile(
            r"(?P<timestamp>\d{8}_\d{6})_?(?P<phone_timestamp>\d{8}_\d{6})?_?(?P<trigger_number>\w{3})-(?P<vehicle_vin>\w+).wav"
        )
        regex_match = pattern.search(file_path)
        if regex_match:
            match_dict = regex_match.groupdict()
            if "timestamp" in regex_match.groupdict():
                match_dict["timestamp"] = match_dict["timestamp"].replace("_", "")
            if "phone_timestamp" in regex_match.groupdict():
                match_dict["phone_timestamp"] = match_dict["phone_timestamp"].replace("_", "")
            return match_dict
        return {}
