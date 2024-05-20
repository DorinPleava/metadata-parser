from abc import ABC, abstractmethod


class MetadataExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> dict:
        pass
