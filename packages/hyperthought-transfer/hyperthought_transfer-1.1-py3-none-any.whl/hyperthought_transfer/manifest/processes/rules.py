"""
Rules engine process.  Matches rules to files as sources for parsers and
targets for metadata parsed from source files.

This is intended to be invoked by a monitor process, e.g. the one in Spike Lab.
(Otherwise, the manifest functions could be called directly, making the process
unnecessary.)
"""

from dataclasses import dataclass
import multiprocessing
import time
from typing import Dict
from typing import Generator
from typing import Optional
from typing import Sequence
from typing import Tuple


# Value received in the process inbox (queue) that tells the process to wrap
# up processing.
STOP_SIGNAL = 1

# Time to sleep between loop iterations, while waiting for files to process.
SLEEP_TIME = 0.5  # seconds


@dataclass
class FileData:
    """
    Definition of file data passed into the process.
    """
    __slots__ = ["file_id", "path"]

    file_id: int
    path: str


class RulesEngineProcess(multiprocessing.Process):
    """
    Rules engine process.  Matches rules to files as sources for parsers and
    targets for metadata parsed from source files.

    Parameters
    ----------
    manifest_file : str
        Path to manifest file.
    rules : sequence of dict
        Rules to be processed.  Will be created when process is started.
    inbox : multiprocessing.Queue
        Used to receive file ids and paths to be processed, as well as
        a stop signal.
        Processing will conclude when the stop signal has been received and
        there is nothing left to process.
    """

    def __init__(
        self,
        manifest_file: str,
        rules: Sequence[Dict],
        inbox: multiprocessing.Queue,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._manifest_file = manifest_file
        self._manifest = None
        self._rules = rules
        self._inbox = inbox

    def _apply_existing_rules_to_new_file_as_target(
        self,
        file_id: str,
        path: str,
    ) -> None:
        """
        Match a new file with existing rules, with the new file as a target.

        This will be done before rules are created from the file.
        When new rules are created, they will be applied to all files,
        including the new file.  With this order of operations, new rules
        will be applied to the new file itself no more than once.

        Parameters
        ----------
        file_id : int
            id of the new file record in the manifest database.
        path : str
            Path to the file on the local system.
        """
        metadata_matches = (
            self._manifest.database.get_rule_matches_for_file_as_target(
                path=path,
            )
        )

        metadata_application_data = []

        for metadata_id in metadata_matches:
            metadata_application_data.append({
                "file_id": file_id,
                "metadata_id": metadata_id,
            })

        self._manifest.database.bulk_load_metadata_application(
            metadata_application_data=metadata_application_data,
        )

    def _create_metadata_with_new_file_as_source(
        self,
        file_id: str,
        path: str,
    ) -> Generator[Tuple[Dict, int], Optional[None], Optional[None]]:
        """
        Create Metadata and associated records when a file matches a rule as
        a source.

        Parameters
        ----------
        file_id : int
            The id of the file of interest.
        path : str
            Path to the file of interest.

        Yields
        ------
        Tuples containing a Rule record (dict) and metadata_id for the
        Metadata record created.
        """
        rule_matches = (
            self._manifest.database.get_rule_matches_for_file_as_source(
                path=path,
            )
        )

        for rule in rule_matches:
            metadata_id = (
                self._manifest.database.create_metadata_for_rule_match(
                    file_id=file_id,
                    rule=rule,
                )
            )
            yield rule, metadata_id

    def _apply_new_rule_to_existing_files_as_targets(
        self,
        path: str,
        rule: Dict,
        metadata_id: int,
    ) -> None:
        """
        Create Metadata and associated records for files matching a new rule
        as a target.

        Parameters
        ----------
        path : str
            Path to the source file.
        rule : dict
            A Rule record.
        metadata_id : int
            The id of the Metadata record created for the rule-parser combo.
        """
        target_file_matches = (
            self._manifest.database.get_files_matching_rule_as_target(
                source_path=path,
                rule=rule,
            )
        )

        metadata_application_data = []

        for file_id in target_file_matches:
            metadata_application_data.append({
                "file_id": file_id,
                "metadata_id": metadata_id,
            })

        self._manifest.database.bulk_load_metadata_application(
            metadata_application_data=metadata_application_data,
        )

    def run(self) -> None:
        """
        Run rule engine to associate files with parsers as sources and targets.
        """
        # Import here to resolve circularity.
        from ...manifest import Manifest
        # Create connection to manifest database.
        self._manifest = Manifest(manifest_file=self._manifest_file)

        # Create rules in manifest.
        for rule in self._rules:
            self._manifest.database.create_rule(**rule)

        stop_signal_received = False

        while not stop_signal_received:
            while not self._inbox.empty():
                file_data = self._inbox.get()

                if file_data == STOP_SIGNAL:
                    stop_signal_received = True
                    continue

                self._apply_existing_rules_to_new_file_as_target(
                    file_id=file_data.file_id,
                    path=file_data.path,
                )

                rule_data = self._create_metadata_with_new_file_as_source(
                    file_id=file_data.file_id,
                    path=file_data.path,
                )

                for rule, metadata_id in rule_data:
                    self._apply_new_rule_to_existing_files_as_targets(
                        path=file_data.path,
                        rule=rule,
                        metadata_id=metadata_id,
                    )

            if not stop_signal_received:
                time.sleep(SLEEP_TIME)
