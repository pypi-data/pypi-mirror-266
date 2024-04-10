"""
Specification for data passed into and out of file binner process.
"""

from dataclasses import dataclass
from enum import IntEnum


class BinSignal(IntEnum):
    # Let the binner process know that a client process has removed all files
    # received in the last bin.
    FILES_REMOVED = 1
    # Let the binner process know that a client process needs a bin.
    BIN_NEEDED = 2
    # Stop the binner process.
    STOP = 3


@dataclass
class FileInput:
    __slots__ = ["process_id", "file_id", "file_size"]

    process_id: str
    file_id: int
    file_size: int


@dataclass
class SignalInput:
    __slots__ = ["process_id", "signal"]

    process_id: str
    signal: int


@dataclass
class BinOutput:
    __slots__ = ["file_ids"]

    file_ids: list
