from dataclasses import dataclass
import datetime
from enum import Enum


class FileType(Enum):
    COMBOX = 1
    SPEECH = 2
    GIN = 3


@dataclass
class FileMetadata:
    account: str = None
    folder: str = None
    path: str = None
    size: int = None

    filetype: str = None
    # filetype: DataExchangeFileType = None
    timestamp: str = None
    vehicle_vin: str = None
    trigger_number: str = None
    trigger_file_hash: str = None
    phone_timestamp: str = None

    created: datetime.datetime = None
    modified: datetime.datetime = None


@dataclass
class BaseMetadata:
    account: str = None
    folder: str = None
    path: str = None
    size: int = None
    created: datetime.datetime = None
    modified: datetime.datetime = None


@dataclass
class SpeechFileMetadata:
    account: str = None
    folder: str = None
    path: str = None
    size: int = None

    timestamp: str = None
    phone_timestamp: str = None
    trigger_number: str = None
    vehicle_vin: str = None

    created: datetime.datetime = None
    modified: datetime.datetime = None
