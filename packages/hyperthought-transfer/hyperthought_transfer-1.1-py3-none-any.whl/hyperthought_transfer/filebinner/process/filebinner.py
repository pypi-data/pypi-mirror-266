"""
Definition of file-binning process.
"""

import multiprocessing
import os
import time
from typing import Dict
from typing import Optional

from .. import data
from .. import database


SLEEP_TIME = 1  # Seconds to sleep while waiting for files to arrive.


class Binner(multiprocessing.Process):
    """
    Create a file binning process.

    Parameters
    ----------
    database_file : str
        Path to database file.
    space_allocation : int
        The amount of space available for a bin, in bytes.
    inbox : multiprocessing.Queue
        Inbox for reception of file data.
        Receives ..data.FileInput or ..data.SignalInput.
    outboxes : dict
        Map process ids to outboxes (multiprocessing.Queue).
        Outboxes for bin information.
        Sends objects of type data.BinOutput.
    """
    def __init__(
        self,
        database_file: str,
        space_allocation: int,
        inbox: multiprocessing.Queue,
        outboxes: Dict[str, multiprocessing.Queue],
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        # Store parameters in data members.
        self._database_file = database_file
        self._available_space = space_allocation
        self._inbox = inbox
        self._process_outboxes = outboxes
        self._process_ids = set(self._process_outboxes.keys())
        # Keep track of the number of processes that receive files and haven't
        # yet indicated that they need more.
        self._processes_with_files = 0
        self._process_needs_bin = {
            process_id: False
            for process_id in self._process_ids
        }

        # Declare other data members.
        self._database = None
        self._bin_id_to_size = {}

    @property
    def database(self) -> Optional[database.Database]:
        return self._database

    def _create_database(self):
        """
        Create a database to keep track of file binning.

        If the database file already exists, it will be overwritten.
        """
        if os.path.exists(self._database_file):
            os.remove(self._database_file)

        connection = database.connect.get_connection(
            binner_path=self._database_file)
        self._database = database.Database(connection=connection)

    def _receive_file(self, file_data: data.FileInput) -> None:
        """Add file to database and update bookkeeping accordingly."""
        # Validate the process id.
        if file_data.process_id not in self._process_ids:
            raise ValueError(f"Unexpected process id: {file_data.process_id}")

        if file_data.file_size > self._available_space:
            raise ValueError(
                f"Unable to handle file with size {file_data.file_size}")

        # Make sure there is at least one bin.
        if not self._bin_id_to_size:
            bin_id = self.database.create_bin()
            self._bin_id_to_size[bin_id] = 0

        # Find the bin into which the file should be placed.
        file_placed = False

        for bin_id in sorted(self._bin_id_to_size.keys()):
            current_size = self._bin_id_to_size[bin_id]

            if current_size + file_data.file_size < self._available_space:
                self._bin_id_to_size[bin_id] += file_data.file_size
                file_placed = True
                break

        if not file_placed:
            bin_id = self.database.create_bin()
            self._bin_id_to_size[bin_id] = file_data.file_size

        self.database.create_file(
            process_id=file_data.process_id,
            manifest_file_id=file_data.file_id,
            file_size=file_data.file_size,
            bin_id=bin_id,
        )

    def _bin_needed(self):
        """Determine whether the client needs a bin."""
        for _, bin_needed in self._process_needs_bin.items():
            if bin_needed:
                return True

        return False

    def _send_bin(self) -> None:
        """Gather files by process and """
        bin_id = self.database.get_next_bin_id()

        # This shouldn't happen.
        if bin_id is None:
            if self._bin_id_to_size:
                raise Exception("No bin id found when bin data exists.")

            # Updates data structures to show that no processes actually need
            # a bin, since no bins exist.
            for process_id in self._process_ids:
                self._process_needs_bin[process_id] = False

            # Don't send a bin if none exists.
            return

        process_id_to_file_ids = self.database.get_bin_data(bin_id=bin_id)
        self._processes_with_files = len(process_id_to_file_ids)

        for process_id, file_ids in process_id_to_file_ids.items():
            outbox = self._process_outboxes[process_id]
            output = data.BinOutput(file_ids=file_ids)
            outbox.put(output)
            self._process_needs_bin[process_id] = False

        # Remove the bin.
        self.database.delete_bin(bin_id=bin_id)
        del self._bin_id_to_size[bin_id]

    def run(self):
        self._create_database()

        stop_signal_received = False

        while not stop_signal_received:
            while not self._inbox.empty():
                message = self._inbox.get()

                if isinstance(message, data.SignalInput):
                    if message.signal == data.BinSignal.FILES_REMOVED:
                        self._processes_with_files -= 1

                        if (
                            self._processes_with_files == 0
                            and
                            self._bin_needed()
                        ):
                            self._send_bin()
                    elif message.signal == data.BinSignal.BIN_NEEDED:
                        self._process_needs_bin[message.process_id] = True

                        if self._processes_with_files == 0:
                            self._send_bin()
                    elif message.signal == data.BinSignal.STOP:
                        stop_signal_received = True
                        break
                else:
                    if not isinstance(message, data.FileInput):
                        raise ValueError(
                            f"Invalid data received in file binner inbox.  "
                            f"Type = {type(message).__name__}"
                        )

                    self._receive_file(file_data=message)

            time.sleep(SLEEP_TIME)
