"""
Define functionality to write to and read from manifest files.

See the Manifest class.
"""

from collections.abc import Sequence
import multiprocessing
import os
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union
from warnings import warn

import hyperthought as ht
from hyperthought.metadata import MetadataItem

from . import database
from .database import TargetRule
from .database import FileFilter
from .database import FileStatus
from .processes.rules import FileData
from .processes.rules import RulesEngineProcess
from .processes.rules import STOP_SIGNAL as RULES_PROCESS_STOP_SIGNAL
from . import utils


MAX_PROCESSES = 60


class PathNotFoundException(Exception):
    pass


class JobDataNotFoundException(Exception):
    pass


def _compute_size_hash_and_end_bytes(file_: Dict) -> Dict:
    """
    Compute size, hash, and end bytes for a file.

    Parameters
    ----------
    file_ : dict
        Database record for the file of interest.

    Returns
    -------
    A dict with keys "id", "size", "hash", and "end_bytes".
    """
    path = file_["path"]
    size = os.path.getsize(path)
    file_hash = utils.get_hash(file_name=path)
    end_bytes = ",".join(str(i) for i in utils.get_end_bytes(path=path))
    return {
        "id": file_["id"],
        "size": size,
        "file_hash": file_hash,
        "end_bytes": end_bytes,
    }


def validate_rules(rules: Optional[Iterable[Dict]] = None) -> None:
    """
    Make sure rules are valid.

    Raise exception if not.

    Parameters
    ----------
    rules : sequence of dict or None
        Rules to be validated.
    """
    if not rules:
        return

    if not isinstance(rules, Sequence):
        raise ValueError("Rules must be a sequence if provided.")

    valid_keys = {
        "source_pattern",
        "parser_class",
        "target_rule_id",
        "target_pattern",
        "name",
    }

    valid_target_rule_ids = {item.value for item in TargetRule}

    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("All rules must be dicts.")

        invalid_keys = set(rule.keys()) - valid_keys

        if invalid_keys:
            raise ValueError(f"Invalid keys for rule: {invalid_keys}.")

        if "source_pattern" not in rule:
            raise ValueError("All rules must have a 'source_pattern'.")

        if (
            not isinstance(rule["source_pattern"], str)
            or
            not rule["source_pattern"]
        ):
            raise ValueError("'source_pattern' must be a non-empty string")

        if "parser_class" not in rule:
            raise ValueError("All rules must have a 'parser_class'.")

        if rule["parser_class"] not in ht.parsers.PARSERS:
            raise ValueError(
                f"{rules['parser_class']} is not a valid value for "
                "'parser_class'."
            )

        if "target_rule_id" not in rule:
            raise ValueError("All rules must have a 'target_rule_id'.")

        if rule["target_rule_id"] not in valid_target_rule_ids:
            raise ValueError(
                f"{rules['target_rule_id']} is not a valid value for "
                "'target_rule_id'.  Must be an integer value for an "
                "instance of the TargetRule enum."
            )

        if (
            "name" in rule
            and
            rule["name"] is not None
            and
            not isinstance(rule["name"], str)
        ):
            raise ValueError("'name' must be a string if provided.")

        if (
            "target_pattern" in rule
            and
            rule["target_pattern"] is not None
            and
            not isinstance(rule["target_pattern"], str)
        ):
            raise ValueError(
                "'target_pattern' must be a string if provided.")


class Manifest:
    """
    File transfer manifest.

    Maintains data on job, paths (files and folders to be transferred),
    parsers, and metadata.

    Parameters
    ----------
    manifest_file : str
        Path to manifest file, which will be a sqlite database.
    overwrite_manifest_file : bool
        If the manifest file already exists, this variable will determine
        whether the existing file will be used or if a new (blank) file
        will overwrite it.
    job_name : str or None
        Must be provided if a new database is created for the manifest.
        The name of the job.  Conventionally, [SOURCE_COMPUTER]_[DATETIME].
    username : str or None
        Must be provided if a new database is created for the manifest.
        The HyperThought username of the user making the upload request.
    workspace_alias : str
        Must be provided if a new database is created for the manifest.
        The alias of the workspace to which the files will be uploaded.
    ignore_path : str or None
        Must be provided if a new database is created for the manifest.
        The (beginning) part of each path that will not be duplicated in
        HyperThought.
    hyperthought_root : str
        Human-readable path to the root HyperThought folder.
        Ex:
            For a file `/a/b/c/d.txt`, ignore_path `/a/b`, and
            hyperthought_root `/x/y`, the path to the file after upload
            will be `/x/y/c/d.txt`.
    rules : sequence of dict or None
        Parsing rules to be added to database.
    common_metadata : sequence of MetadataItem
        Metadata common to all files and folders in the job.

    All parameters except manifest_file and rules will be ignored if
    an existing database is opened without being rewritten.
    """

    def __init__(
        self,
        manifest_file: str,
        overwrite_manifest_file: bool = False,
        job_name: Optional[str] = None,
        username: Optional[str] = None,
        workspace_alias: Optional[str] = None,
        ignore_path: Optional[str] = None,
        hyperthought_root: str = "/",
        rules: Optional[Iterable[Dict]] = None,
        common_metadata: Optional[Iterable[MetadataItem]] = None,
        avoid_duplicates: Optional[bool] = False,
    ) -> None:
        self._manifest_file = manifest_file
        self._job_name = job_name
        self._username = username
        self._workspace_alias = workspace_alias
        self._ignore_path = (
            utils.clean_path(ignore_path) if ignore_path else ignore_path
        )

        if (
            isinstance(self._ignore_path, str)
            and
            self._ignore_path.endswith(":")
        ):
            self._ignore_path += os.path.sep

        self._hyperthought_root = hyperthought_root.replace("\\", "/")
        # TODO:  Validate common metadata.
        self._common_metadata = common_metadata
        validate_rules(rules)  # Will throw an Exception if not valid.
        self._rules_process: Optional[RulesEngineProcess] = None
        self._rules_process_inbox: Optional[multiprocessing.Queue] = None
        self._avoid_duplicates = avoid_duplicates
        self._hyperthought_root_id_path = ","
        self._database: Optional[database.Database] = None
        self._file_info_computed = False

        if os.path.exists(self._manifest_file):
            if not os.path.isfile(manifest_file):
                raise ValueError(f"{manifest_file} is not a file")

            if overwrite_manifest_file:
                self._create_database(rules=rules)
            else:
                self._set_database(rules=rules)
        else:
            self._create_database(rules=rules)

    def _create_database(self, rules: Optional[Iterable[Dict]] = None) -> None:
        """Create new database.  Load job information."""
        self._validate_job_data()
        connection = database.connect.get_connection(
            manifest_path=self._manifest_file,
            overwrite=True,
        )
        self._database = database.Database(connection=connection)
        self.database.create_job_data(
            job_name=self._job_name,
            username=self._username,
            workspace_alias=self._workspace_alias,
            ignore_path=self.ignore_path,
            hyperthought_root=self._hyperthought_root,
            avoid_duplicates=self._avoid_duplicates,
        )
        self._create_hyperthought_root()

        if self._common_metadata:
            self.database.create_or_update_common_metadata(
                metadata=self._common_metadata,
            )

        if rules:
            self._rules_process_inbox = multiprocessing.Queue()
            self._rules_process = RulesEngineProcess(
                manifest_file=self._manifest_file,
                rules=rules,
                inbox=self._rules_process_inbox,
            )
            self._rules_process.start()

    def _create_hyperthought_root(self) -> None:
        """Create File records for all hyperthought_root folders."""
        ht_id_path = ","
        stripped_root = self.hyperthought_root.strip("/")

        if not stripped_root:
            self._hyperthought_root_id_path = ht_id_path
            return

        root_folders = stripped_root.split("/")
        file_data = []

        for folder_name in root_folders:
            ht_id = utils.generate_id()
            file_data.append(
                {
                    "name": folder_name,
                    "hyperthought_id": ht_id,
                    "hyperthought_id_path": ht_id_path,
                    "is_folder": True,
                    "path": None,
                    "end_bytes": None,
                    "size": None,
                    "file_hash": None,
                }
            )
            ht_id_path = f"{ht_id_path}{ht_id},"

        self.database.bulk_load_files(file_data=file_data)
        self._hyperthought_root_id_path = ht_id_path

    def _set_database(self, rules: Optional[Iterable[Dict]] = None) -> None:
        """Connect to existing database."""
        connection = database.connect.get_connection(
            manifest_path=self._manifest_file,
            overwrite=False,
        )
        self._database = database.Database(connection=connection)
        job_data = self.database.get_job_data()

        if job_data is None:
            raise JobDataNotFoundException(
                f"No job data in {self._manifest_file}")

        self._job_name = job_data["job_name"]
        self._username = job_data["username"]
        self._workspace_alias = job_data["workspace_alias"]
        self._ignore_path = job_data["ignore_path"]
        self._hyperthought_root = job_data["hyperthought_root"]
        self._avoid_duplicates = job_data["avoid_duplicates"]

        stripped_root = self._hyperthought_root.strip("/")

        if not stripped_root:
            return

        def get_hyperthought_id(
            name: str,
            hyperthought_id_path: str
        ) -> Optional[str]:
            """Get a hyperthought_id given name and hyperthought_id_path."""
            file_ = self.database.get_file(
                name=name,
                hyperthought_id_path=hyperthought_id_path,
            )

            if not file_:
                return None

            return file_["hyperthought_id"]

        root_folders = stripped_root.split("/")
        hyperthought_id_path = ","

        for folder_name in root_folders:
            hyperthought_id = get_hyperthought_id(
                name=folder_name,
                hyperthought_id_path=hyperthought_id_path,
            )

            if not hyperthought_id:
                hyperthought_id = utils.generate_id()
                self.database.create_file(
                    name=folder_name,
                    is_folder=True,
                    hyperthought_id=hyperthought_id,
                    hyperthought_id_path=hyperthought_id_path,
                )

            hyperthought_id_path += hyperthought_id + ","

        self._hyperthought_root_id_path = hyperthought_id_path

        if rules:
            self._rules_process_inbox = multiprocessing.Queue()
            self._rules_process = RulesEngineProcess(
                manifest_file=self._manifest_file,
                rules=rules,
                inbox=self._rules_process_inbox,
            )
            self._rules_process.start()

    def _validate_job_data(self) -> None:
        """
        Validate job data parameters (to constructor).

        Called from _create_database.
        """
        if not self._job_name or not isinstance(self._job_name, str):
            raise ValueError("job_name must be a non-empty string")

        if not self._username or not isinstance(self._username, str):
            raise ValueError("username must be a non-empty string")

        if (
            not self._workspace_alias
            or
            not isinstance(self._workspace_alias, str)
        ):
            raise ValueError("workspace_id must be a non-empty string")

        # TODO:  Make code below work properly when creating db from json.
        # if (
        #     self._ignore_path is not None
        #     and
        #     not os.path.isdir(self._ignore_path)
        # ):
        #     raise ValueError(
        #         "ignore_path_prefix must be a directory if provided")

        if (
            not self._hyperthought_root
            or
            not isinstance(self._hyperthought_root, str)
        ):
            raise ValueError("hyperthought_root must be a string")

        if not self._hyperthought_root.startswith("/"):
            raise ValueError("hyperthought_root must start with '/'")

        if not isinstance(self._avoid_duplicates, bool):
            raise ValueError("avoid_duplicates must be a bool")

    @property
    def database(self) -> database.Database:
        return self._database

    @property
    def common_metadata(self) -> List[MetadataItem]:
        return ht.metadata.from_api_format(
            self.database.get_common_metadata())

    @common_metadata.setter
    def common_metadata(self, metadata: List[MetadataItem]) -> None:
        self._validate_metadata(metadata)
        self.database.create_or_update_common_metadata(metadata=metadata)

    @property
    def ignore_path(self) -> Optional[str]:
        return self._ignore_path

    @property
    def hyperthought_root(self) -> str:
        return self._hyperthought_root

    @property
    def hyperthought_root_id_path(self) -> str:
        return self._hyperthought_root_id_path

    @hyperthought_root_id_path.setter
    def hyperthought_root_id_path(self, value: str) -> None:
        self._hyperthought_root_id_path = value

    @property
    def file_info_computed(self) -> bool:
        return self._file_info_computed

    @property
    def avoid_duplicates(self) -> bool:
        return self._avoid_duplicates

    def _validate_metadata(self, metadata: List[MetadataItem]) -> None:
        """
        Make sure metadata is a list of MetadataItem objects.

        An exception will be raised if the metadata is not valid.
        """
        if not isinstance(metadata, Sequence) or isinstance(metadata, str):
            raise ValueError("metadata must be a non-string sequence")

        for item in metadata:
            if not isinstance(item, MetadataItem):
                raise ValueError(
                    "all elements of metadata must be instances of "
                    "hyperthought.metadata.MetadataItem"
                )

    def add_rule(
        self,
        source_pattern: str,
        parser_class: str,
        target_rule: TargetRule,
        target_pattern: Optional[str] = None,
        name: Optional[str] = None,
    ) -> int:
        """
        Create a rule for specifying metadata extraction and application.

        Parameters
        ----------
        source_pattern : str
            A pattern which the source file, the file from which metadata
            will be extracted, must satisfy.
        parser_class : str
            The name of a parser class.
        target_rule : TargetRule
            Relationship between source file and target files/folders.
        target_pattern : str
            A pattern which a target file/folder must satisfy in order for the
            extracted metadata to be applied.
        name : str
            A name for the rule to be displayed in the UI.

        Patterns must work with the SQL LIKE operator.
        For example, the '%' character will match any number of characters.

        Returns
        -------
        The id of the last row created.
        """
        return self.database.create_rule(
            source_pattern=source_pattern,
            parser_class=parser_class,
            target_rule=target_rule,
            target_pattern=target_pattern,
            name=name,
        )

    def add_rules(self, rule_data: List[Dict]) -> None:
        """
        Bulk add rules.

        Parameters
        ----------
        rule_data : list
            contains Rule entries with the following keys to be committed
            to the database:
                source_pattern : str
                    Pattern a source file needs to match.
                parser_class : str
                    Name of a parser class in the hyperthought package.
                target_rule_id : int
                    id of a TargetRule record.
                target_pattern : str
                    Pattern a target file needs to match.
                name : str
                    Name for a rule.  (Used only in the UI.)
        """
        self.database.bulk_load_rules(rule_data=rule_data)

    def add_path(self, path: str) -> None:
        """
        Add a path to the manifest.

        Ancestor folders will be created as needed.
        """
        # TODO:  Consider removing this function and using add_paths instead.
        path = utils.clean_path(path)
        self._validate_path(path)

        # Exit early if the path has already been added.
        if self.has_path(path):
            return

        is_folder = os.path.isdir(path)

        if not is_folder:
            self._file_info_computed = False

        # Get a list of ancestor folders.
        len_ignorepath = (
            0
            if self._ignore_path is None
            else len(self._ignore_path)
        )

        ancestor_folders = (
            path[len_ignorepath:].strip(os.path.sep).split(os.path.sep)
        )[:-1]
        n_ancestors = len(ancestor_folders)
        ancestor_found = False

        # Determine how many ancestors need to be created.
        # Go backwards until an existing folder is found.
        # break_index will be one more than the index of the last folder that
        # already exists, or 1 if no folders exist.
        break_index = None

        for break_index in reversed(range(1, n_ancestors + 1)):
            ancestor_folders_to_join = ancestor_folders[0:break_index]
            ancestor_path = (
                os.path.join(self._ignore_path, *ancestor_folders_to_join)
                if self._ignore_path is not None
                else os.path.join(*ancestor_folders_to_join)
            )

            if self.has_path(ancestor_path):
                ancestor_found = True
                break

        # Get the hyperthought id path starting with an existing folder,
        # if present, or the root id path.
        if ancestor_found:
            # Maintain the invariant that break_index is the index of the
            # first folder that *doesn't* exist.
            break_index += 1
            ancestor_id = self.database.get_file_id(path=ancestor_path)
            ancestor = self.database.get_file(file_id=ancestor_id)
            ht_id_path = (
                f"{ancestor['hyperthought_id_path']}"
                f"{ancestor['hyperthought_id']},"
            )
        else:
            ht_id_path = self.hyperthought_root_id_path

        # Variable for bulk file record creation.
        file_data = []

        # Add folders that need to be created.
        if break_index is not None:
            for folder_index in range(break_index, n_ancestors + 1):
                ancestor_folders_to_join = ancestor_folders[:folder_index]
                folder_path = (
                    os.path.join(self._ignore_path, *ancestor_folders_to_join)
                    if self._ignore_path is not None
                    else os.path.join(*ancestor_folders_to_join)
                )
                ht_id = utils.generate_id()
                file_data.append(
                    {
                        "name": os.path.basename(folder_path),
                        "hyperthought_id": ht_id,
                        "hyperthought_id_path": ht_id_path,
                        "is_folder": True,
                        "path": folder_path,
                        "end_bytes": None,
                        "size": None,
                        "file_hash": None,
                    }
                )
                ht_id_path = f"{ht_id_path}{ht_id},"

        # Add the file/folder itself.
        file_data.append(
            {
                "name": os.path.basename(path),
                # Folders should have ids, while files shouldn't.
                "hyperthought_id": utils.generate_id() if is_folder else None,
                "hyperthought_id_path": ht_id_path,
                "is_folder": is_folder,
                "path": path,
                "end_bytes": None,
                "size": None,
                "file_hash": None,
            }
        )

        # Create all records.
        # NOTE:  ids will be added to the list elements by the bulk loader.
        self.database.bulk_load_files(file_data=file_data)

        if self._rules_process:
            for item in file_data:
                self._rules_process_inbox.put(
                    FileData(
                        file_id=item["id"],
                        path=item["path"],
                    )
                )

    def add_paths(self, paths: Iterable[str]) -> None:
        """
        Add paths to the manifest.

        Ancestor folders will be created as needed.
        """
        if not paths:
            return

        # Sanitize input.
        paths_to_add = {utils.clean_path(path) for path in paths}

        # Validate input.
        for path in paths_to_add:
            self._validate_path(path)

        len_ignorepath = (
            0
            if self._ignore_path is None
            else len(self._ignore_path)
        )

        def get_ancestor_paths(
            path: str
        ) -> Generator[Optional[str], Optional[str], None]:
            """
            Get ancestor folders for each path, ignoring any ancestors
            in self._ignore_path.
            """
            ancestor_tokens = (
                path[len_ignorepath:].strip(os.path.sep).split(os.path.sep)
            )[:-1]

            for index in range(1, len(ancestor_tokens) + 1):
                yield os.path.join(
                    self._ignore_path,
                    *ancestor_tokens[:index]
                )

        # Use the inner function defined above to add ancestor paths
        # to clean_paths.
        for path in list(paths_to_add):
            for ancestor_path in get_ancestor_paths(path):
                paths_to_add.add(ancestor_path)

        existing_paths = set()
        folder_path_to_hyperthought_id = {}

        for file_ in self.database.get_files(paths=paths_to_add):
            existing_paths.add(file_["path"])

            if file_["is_folder"]:
                folder_path_to_hyperthought_id[file_["path"]] = (
                    file_["hyperthought_id"])

        # Add ids for existing folders to the lookup.
        for path in paths_to_add:
            is_folder = os.path.isdir(path)

            if path not in existing_paths and is_folder:
                folder_path_to_hyperthought_id[path] = utils.generate_id()

        def get_hyperthought_id(path: str) -> Union[str, None]:
            """
            Get a hyperthought id for a file or folder.

            The result will be an id for a folder, None for a file.
            folder_path_to_hyperthought_id will be used.
            """
            if path in folder_path_to_hyperthought_id:
                return folder_path_to_hyperthought_id[path]
            else:
                return None

        def get_hyperthought_id_path(path: str) -> str:
            """
            Get a HyperThought id path (content.path) for a file/folder.

            Use the folder_path_to_hyperthought_id lookup.
            """
            hyperthought_id_path = self.hyperthought_root_id_path

            for ancestor_path in get_ancestor_paths(path):
                ancestor_hyperthought_id = (
                    folder_path_to_hyperthought_id[ancestor_path])
                hyperthought_id_path += f"{ancestor_hyperthought_id},"

            return hyperthought_id_path

        paths_to_create = paths_to_add - existing_paths
        file_data = []

        for path in paths_to_create:
            file_data.append({
                "name": os.path.basename(path),
                "hyperthought_id": get_hyperthought_id(path),
                "hyperthought_id_path": get_hyperthought_id_path(path),
                "is_folder": os.path.isdir(path),
                "path": path,
                "end_bytes": None,
                "size": None,
                "file_hash": None,
            })

        # Create all file records.
        # NOTE:  file ids will be added in place by the bulk load method.
        self.database.bulk_load_files(file_data=file_data)

        if self._rules_process:
            for item in file_data:
                self._rules_process_inbox.put(
                    FileData(
                        file_id=item["id"],
                        path=item["path"],
                    )
                )

    def apply_metadata(
        self,
        metadata_id: int,
        apply_to_file_ids: List[int],
    ) -> None:
        """
        Apply metadata to files.

        Parameters
        ----------
        metadata_id : int
            The id of the Metadata record of interest.
        apply_to_file_ids : list of int
            File ids to which the metadata should be applied.
        """
        metadata_application_data = [
            {
                "metadata_id": metadata_id,
                "file_id": file_id
            }
            for file_id in apply_to_file_ids
        ]
        self.database.bulk_load_metadata_application(
            metadata_application_data=metadata_application_data)

    def remove_path(self, path: str) -> None:
        """
        Remove a path from the manifest.

        Parameters
        ----------
        path : str
            The path to be removed.
        """
        ids_to_remove = [self.get_path_id(path)]

        if os.path.isdir(path):
            ids_to_remove.extend(
                file_["id"]
                for file_ in self.get_progeny(folder_path=path)
            )

        for id_ in ids_to_remove:
            self.database.delete_file(file_id=id_)

    def _validate_path(self, path: str) -> None:
        """
        Determine whether a path is valid.

        An exception will be raised if the path is not valid.
        """
        path = utils.clean_path(path)

        if self.ignore_path and not path.startswith(self.ignore_path):
            raise ValueError(
                f"path '{path}' does not begin with " f"'{self.ignore_path}'"
            )

        if (
            os.path.islink(path)
            or
            not (os.path.isfile(path) or os.path.isdir(path))
        ):
            raise ValueError(
                "path must be a file or directory (links not allowed)")

    def has_path(self, path: str) -> bool:
        """Determine whether a path has already been added."""
        # TODO:  Consider removing this function and always using has_paths.
        path = utils.clean_path(path)
        file_id = self.database.get_file_id(path=path)
        return file_id is not None

    def get_path_id(self, path: str) -> int:
        """Get internal id associated with a path."""
        path = utils.clean_path(path)
        path_id = self.database.get_file_id(path=path)

        if path_id is None:
            raise PathNotFoundException(
                f"path '{path}' has not been added to the manifest"
            )

        return path_id

    def get_file(self, file_id: str) -> Dict:
        """Get file data given a file id."""
        return self.database.get_file(file_id=file_id)

    def get_progeny(self, folder_path: str) -> List[Dict]:
        """
        Get information on files under a given path in the manifest.

        This will search the manifest for such files, not the local file
        system.

        Parameters
        ----------
        folder_path : str
            The folder of interest.

        Returns
        -------
        A list of file records for paths under the given folder.
        """
        return self.database.get_progeny(folder_path=folder_path)

    def get_rules(
        self,
        file_id: Optional[int] = None,
        parser: Optional[str] = None,
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Get a list of rules, possibly sorted by file and/or parser.

        Parameters
        ----------
        file_id : int or None
            The id of a particular file.
        parser : str
            A parser class name.

        Returns
        -------
        A list of Rule records, filtered to be relevant to a particular file
        or parser.
        """
        for rule in self.database.get_rules(file_id=file_id, parser=parser):
            yield rule

    def _validate_parser(self, parser_class_name: str) -> None:
        if parser_class_name not in ht.parsers.PARSERS:
            raise ValueError(f"parser '{parser_class_name}' not found")

    def add_parser(
        self,
        file_id: int,
        parser_class_name: str,
        apply_to_file_ids: List[int],
    ) -> None:
        """
        Add a parser application to the manifest.

        Parameters
        ----------
        file_id : int
            The id of the file to be parsed.
        parser_class_name : str
            The class name of the parser to be used.
        apply_to_file_ids : list of int
            Internal ids of files/folders to which the parsed metadata will
            be applied.
        """
        if not apply_to_file_ids:
            raise ValueError("apply_to_file_ids must not be empty")

        self._validate_parser(parser_class_name)
        metadata_id = self.database.create_metadata(file_id=file_id)
        metadata_application_data = [
            {
                "metadata_id": metadata_id,
                "file_id": file_id,
            }
            for file_id in apply_to_file_ids
        ]
        self.database.bulk_load_metadata_application(
            metadata_application_data=metadata_application_data
        )
        self.database.create_parser(
            file_id=file_id,
            parser_class=parser_class_name,
            metadata_id=metadata_id,
        )

    def get_parsers(
        self,
        file_id: int,
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Get all parsers to be applied to a specified file.

        Parameters
        ----------
        file_id : int
            The id of the file of interest.

        Yields
        ------
        Dicts containing data from the Parser table.
        """
        for parser in self.database.get_parsers_for_file(file_id=file_id):
            yield parser

    def add_metadata(
        self,
        file_id: int,
        metadata: List[MetadataItem],
        apply_to_file_ids: List[int],
    ) -> int:
        """
        Deprecated.  Use add_or_update_file_specific_metadata instead.
        """
        warn(
            (
                "Manifest.add_metadata is deprecated. "
                "Use Manifest.add_or_update_file_specific_metadata instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_or_update_file_specific_metadata(
            file_id=file_id,
            metadata=metadata,
            apply_to_file_ids=apply_to_file_ids,
        )

    def add_or_update_file_specific_metadata(
        self,
        file_id: int,
        metadata: List[MetadataItem],
        apply_to_file_ids: List[int],
    ) -> int:
        """
        Add or update file-specific metadata to the manifest.

        Any previously added file-specific metadata will be removed and
        replaced.

        Parameters
        ----------
        metadata : list of MetadataItem
            The metadata of interest.
        apply_to_file_ids : list of str
            Internal ids of files/folders to which the metadata will be
            applied.

        Returns
        -------
        The id of the metadata record that was created.
        """
        self._validate_metadata(metadata)

        metadata_id = self.database.get_file_specific_metadata_id(
            file_id=file_id)

        if metadata_id is not None:
            self.database.delete_metadata(metadata_id=metadata_id)

        metadata_id = self.database.create_metadata(
            file_id=file_id,
            metadata=metadata,
        )
        metadata_application_data = [
            {"metadata_id": metadata_id, "file_id": file_id}
            for file_id in apply_to_file_ids
        ]
        self.database.bulk_load_metadata_application(
            metadata_application_data=metadata_application_data
        )
        return metadata_id

    def get_metadata(self, metadata_id: int) -> List[MetadataItem]:
        """
        Get metadata given a metadata id.

        Parameters
        ----------
        metadata_id: int
            The id of the Metadata record of interest.

        Returns
        -------
        A list of MetadataItem objects.
        """
        metadata_record = self.database.get_metadata(metadata_id=metadata_id)
        metadata = metadata_record["metadata"]
        return ht.metadata.from_api_format(metadata=metadata)

    def delete_metadata(self, metadata_id: int) -> None:
        """Remove a Metadata record."""
        self.database.delete_metadata(metadata_id=metadata_id)

    def delete_metadata_application(self, metadata_id: int) -> None:
        """Remove MetadataApplication records associated with a metadata id."""
        self.database.delete_metadata_application(metadata_id=metadata_id)

    def delete_parser(self, parser_id: int) -> None:
        """Delete a parser."""
        self.database.delete_parser(parser_id=parser_id)

    def get_file_specific_metadata_id(self, file_id: int) -> Optional[int]:
        """
        Get the id of a metadata record corresponding to file-specific metadata
        for a given file.

        Parameters
        ----------
        file_id : int
            The id of the File of interest.

        Returns
        -------
        The of the Metadata record containing file-specific metadata for the
        file, or None if no such record exists.

        Exceptions
        ----------
        FileSpecificMetadataUniquenessException
            Raised if more than one record of file-specific metadata (records
            not associated with parsers) are found.
        """
        return self.database.get_file_specific_metadata_id(file_id=file_id)

    def update_metadata(
        self,
        metadata_id: int,
        metadata: List[MetadataItem],
    ) -> None:
        """
        Update a metadata record.

        Parameters
        ----------
        metadata_id : int
            id of the metadata record to be updated.
        metadata : list of MetadataItem
            New metadata for the record.  Any previous value will be completely
            overwritten.  The client will be responsible for merging old and
            new metadata, if that is desired.
        """
        api_formatted_metadata = ht.metadata.to_api_format(metadata)
        self.database.update_metadata(
            id_=metadata_id,
            updates={
                "metadata": api_formatted_metadata,
            },
        )

    def to_json(self, compute_file_info: bool = True) -> Dict:
        """Convert manifest database to JSON and return results."""
        if compute_file_info and not self.file_info_computed:
            self.compute_file_info()

        output = {}

        # Create the job section of the manifest.
        job_data = self.database.get_job_data()
        output["job"] = {
            "name": job_data["job_name"],
            "username": job_data["username"],
            "workspaceAlias": job_data["workspace_alias"],
            "hyperthoughtRootPath": job_data["hyperthought_root"],
            "ignorePathPrefix": job_data["ignore_path"],
            "avoidDuplicates": job_data["avoid_duplicates"],
        }

        # Create the files section.
        output_files = []
        files = self.database.get_all_files()

        for file_ in files:
            item = {
                "id": file_["hyperthought_id"],
                "path": file_["path"],
            }

            if file_["is_folder"]:
                item.update({
                    "type": "folder",
                    "size": None,
                    "hash": None,
                    "endBytes": None,
                })
            else:
                end_bytes = [int(s) for s in file_["end_bytes"].split(",")]
                item.update({
                    "type": "file",
                    "size": file_["size"],
                    "hash": file_["file_hash"],
                    "endBytes": end_bytes,
                })

            output_files.append(item)

        # Create the metadata section.
        metadata_id_to_parsers = {}
        parsers = self.database.get_all_parsers()

        for parser in parsers:
            metadata_id = parser["metadata_id"]
            value = {
                "parserClass": parser["parser_class"],
                "parseFileId": parser["hyperthought_id"],
                "applyToFileIds": [],
            }
            metadata_id_to_parsers[metadata_id] = value

        # Map metadata id to file-specific metadata.
        metadata_id_to_specific = {}
        specified_metadata = self.database.get_all_metadata(file_specific=True)

        for metadata in specified_metadata:
            metadata_id = metadata["id"]
            value = {
                "metadata": metadata["metadata"],
                "applyToFileIds": [],
            }
            metadata_id_to_specific[metadata_id] = value

        metadata_applications = self.database.get_all_metadata_application()

        for metadata_application in metadata_applications:
            metadata_id = metadata_application["metadata_id"]
            file_id = metadata_application["hyperthought_id"]

            if metadata_id in metadata_id_to_parsers:
                metadata_id_to_parsers[metadata_id]["applyToFileIds"].append(
                    file_id)

            if metadata_id in metadata_id_to_specific:
                metadata_id_to_specific[metadata_id]["applyToFileIds"].append(
                    file_id)

        output["metadata"] = {
            "parsing": list(metadata_id_to_parsers.values()),
            "fileSpecific": list(metadata_id_to_specific.values()),
            "common": self.database.get_common_metadata(),
        }

        return output

    def get_file_page(self, start: int, length: int) -> List[Dict]:
        """
        Get a single page of file results.

        Indexing is effectively zero-based.

        Parameters
        ----------
        start : int
            The start index for the page.
        length : int
            The page length.

        Returns
        -------
        List of dicts containing file information.
        """
        return self.database.get_file_page(start=start, length=length)

    def _compute_file_info_with_pool(
        self,
        n_processes: Optional[int] = None,
    ) -> None:
        """Compute file size, hash, and end bytes using a process pool."""
        if (
            n_processes is not None
            and
            not (isinstance(n_processes, int) and n_processes > 0)
        ):
            raise ValueError(
                "n_processes must be a positive integer if provided")

        if n_processes is None:
            n_processes = multiprocessing.cpu_count() * 2

        n_processes = min(n_processes, MAX_PROCESSES)
        files = self.database.get_all_files(filter_=FileFilter.FILES_ONLY)
        pool = multiprocessing.Pool(processes=n_processes)
        all_updates = pool.map(_compute_size_hash_and_end_bytes, files)
        pool.close()
        pool.join()

        for updates in all_updates:
            id_ = updates.pop("id")
            self.database.update_file(id_=id_, updates=updates)

    def _compute_file_info_without_pool(self) -> None:
        """Compute file hashes and end bytes in the current process."""
        files = self.database.get_all_files(filter_=FileFilter.FILES_ONLY)

        for file_ in files:
            updates = _compute_size_hash_and_end_bytes(file_=file_)
            id_ = updates.pop("id")
            self.database.update_file(id_=id_, updates=updates)

    def compute_file_info(
        self,
        use_pool: bool = True,
        n_processes: Optional[int] = None,
    ) -> None:
        """Compute hash and end_bytes for each file in the manifest."""
        if use_pool:
            self._compute_file_info_with_pool(n_processes=n_processes)
        else:
            self._compute_file_info_without_pool()

        self._file_info_computed = True

    def get_total_size(self) -> int:
        """Get the sum of file sizes for all files in the manifest."""
        return self.database.get_total_size()

    def get_metadata_application(
        self,
        metadata_id: int,
        filter_: FileFilter = FileFilter.ALL,
    ) -> Generator[int, Optional[None], Optional[None]]:
        """
        Get ids for files to which metadata will be applied.

        Parameters
        ----------
        metadata_id : int
            Id of the Metadata record of interest.
        filter_ : MetadataApplicationFilter
            Enum instance used to specify filter for results.

        Yields
        ------
        Ids for files to which metadata will be applied.
        """
        generator = self.database.get_metadata_application(
            metadata_id=metadata_id,
            filter_=filter_,
        )

        for file_id in generator:
            yield file_id

    def close(self, compute_file_info: bool = True) -> None:
        """
        Close the manifest (database).

        Parameters
        ----------
        compute_file_info : bool
            If True, update file records to include sizes, hashes,
            and end bytes.
        """
        if self._rules_process:
            self._rules_process_inbox.put(RULES_PROCESS_STOP_SIGNAL)

        if compute_file_info and not self.file_info_computed:
            self.compute_file_info()

        self.database.connection.close()

        # NOTE:  The rules process has its own database connection.
        if self._rules_process:
            self._rules_process.join()

    def get_all_files(
        self,
        filter_: FileFilter = FileFilter.ALL
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Get all files and/or folders in the job.

        Yields
        ------
        Dicts containing information on all files and/or folders in the job.
        """
        files = self.database.get_all_files(filter_=filter_)

        for file_ in files:
            yield file_

    def get_files(
        self,
        file_ids: Optional[Iterable[int]] = None,
        paths: Optional[Iterable[str]] = None
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Get all file records corresponding a list of ids or paths.

        Parameters
        ----------
        file_ids : list of int
            Database ids for the files of interest.
        paths : list of str
            Paths for files of interest.
            Must be provided if file_ids is not.

        Returns
        -------
        A list of dicts containing file record data.
        """
        for file_ in self.database.get_files(file_ids=file_ids, paths=paths):
            yield file_

    def get_metadata_information(
        self,
        file_ids: Iterable[int],
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Get data to be used with the update-metadata endpoint.

        Parameters
        ----------
        file_ids : list-like of int
            Internal file ids for files of interest.

        Yields
        ------
        A dict with keys "file_id", "metadata_id", "hyperthought_id", and
        "metadata".  This information can be used to build data structures
        mapping file ids to lists of metadata ids, file ids to hyperthought
        ids, and metadata ids to metadata.  These data structures, in turn,
        can be used to build a list of dicts having keys "documentId"
        and "metadata" (combined for each file), which can be used as input
        to the update-metadata HyperThought endpoint.
        """
        yield from self.database.get_metadata_information(file_ids=file_ids)

    def update_file_status(
        self,
        file_ids: Iterable[int],
        status: FileStatus,
    ) -> None:
        """
        Update status for multiple files.

        All files will be given the same status.

        Parameters
        ----------
        file_ids : list-like of int
            Sequence of file ids.
        status : FileStatus
            Status to set for all files.
        """
        self.database.update_file_status(file_ids=file_ids, status=status)


def from_json(manifest_data: Dict, manifest_database_file: str) -> Manifest:
    """
    Create and return a manifest with the given (JSON) data.

    Convert JSON to SQLite and store in the specified database file.

    Parameters
    ----------
    manifest_data : dict
        In-memory JSON-formatted manifest data.
    manifest_database_file : str
        Path to the database file where the data will be stored.
        If the file already exists, it will be overwritten to contain the
        new data.

    Returns
    -------
    A Manifest object with a connection to the database file.
    The caller will be responsible for closing the connection via the `close`
    method.
    """
    # Create the Manifest object.
    kwargs = {
        "manifest_file": manifest_database_file,
        "overwrite_manifest_file": True,
        "job_name": manifest_data["job"]["name"],
        "username": manifest_data["job"]["username"],
        "workspace_alias": manifest_data["job"]["workspaceAlias"],
        "ignore_path": manifest_data["job"]["ignorePathPrefix"],
        "hyperthought_root": manifest_data["job"]["hyperthoughtRootPath"],
    }

    if "avoid_duplicates" in manifest_data["job"]:
        kwargs["avoid_duplicates"] = manifest_data["job"]["avoid_duplicates"]

    manifest = Manifest(**kwargs)

    # Add files to the manifest.
    manifest_files = sorted(
        manifest_data["files"],
        key=lambda item: item["path"],
    )
    len_ignore_path = len(manifest.ignore_path) if manifest.ignore_path else 0
    path_to_hyperthought_id = {}
    manifest_id_to_hyperthought_id = {}
    file_data = []

    for manifest_file in manifest_files:
        path = utils.clean_path(manifest_file["path"])
        relative_path = path[len_ignore_path:].replace("\\", "/").strip("/")
        hyperthought_id = utils.generate_id()
        manifest_id_to_hyperthought_id[manifest_file["id"]] = hyperthought_id
        path_to_hyperthought_id[relative_path] = hyperthought_id
        is_folder = manifest_file["type"] == "folder"

        if not is_folder:
            end_bytes = ",".join(str(i) for i in manifest_file["endBytes"])
        else:
            end_bytes = None

        path_tokens = relative_path.split("/")
        hyperthought_id_path = manifest.hyperthought_root_id_path

        for index in range(0, len(path_tokens) - 1):
            parent_path = "/".join(path_tokens[:(index + 1)])

            if parent_path not in path_to_hyperthought_id:
                full_parent_path = f"{manifest.ignore_path}/{parent_path}"
                raise ValueError(f"missing parent path: {full_parent_path}")

            parent_id = path_to_hyperthought_id[parent_path]
            hyperthought_id_path = f"{hyperthought_id_path}{parent_id},"

        # TODO:  Add validation for manifest data:  size, hash.

        file_data.append({
            "name": os.path.basename(relative_path),
            "hyperthought_id": hyperthought_id,
            "hyperthought_id_path": hyperthought_id_path,
            "is_folder": is_folder,
            "path": path,
            "end_bytes": end_bytes,
            "size": manifest_file["size"],
            "file_hash": manifest_file["hash"],
        })

    manifest.database.bulk_load_files(file_data=file_data)
    ht_to_db_id = {
        item["hyperthought_id"]: item["id"]
        for item in file_data
    }
    manifest_id_to_database_id = {
        manifest_id: ht_to_db_id[manifest_id_to_hyperthought_id[manifest_id]]
        for manifest_id in manifest_id_to_hyperthought_id
    }

    # Add parsers to the manifest.
    for parser in manifest_data["metadata"]["parsing"]:
        file_id = manifest_id_to_database_id[parser["parseFileId"]]
        apply_to_file_ids = [
            manifest_id_to_database_id[id_] for id_ in parser["applyToFileIds"]
        ]
        manifest.add_parser(
            file_id=file_id,
            parser_class_name=parser["parserClass"],
            apply_to_file_ids=apply_to_file_ids,
        )

    # Add file-specific metadata.
    for metadata_item in manifest_data["metadata"]["fileSpecific"]:
        metadata = ht.metadata.from_api_format(
            metadata=metadata_item["metadata"])
        apply_to_file_ids = [
            manifest_id_to_database_id[id_]
            for id_ in metadata_item["applyToFileIds"]
        ]

        if not apply_to_file_ids:
            continue

        # The file id associated with the metadata doesn't matter.
        # It could be any one of the files.
        file_id = apply_to_file_ids[0]

        manifest.add_or_update_file_specific_metadata(
            file_id=file_id,
            metadata=metadata,
            apply_to_file_ids=apply_to_file_ids,
        )

    # Add common metadata.
    manifest.common_metadata = ht.metadata.from_api_format(
        manifest_data["metadata"]["common"]
    )

    return manifest
