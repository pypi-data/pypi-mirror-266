"""
Database functionality for a file transfer manifest.

An object of class Database is available via the `database` property of a
manifest object.
"""

from enum import Enum
from enum import IntEnum
import os
import sqlite3
from sqlite3 import Connection
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional

import hyperthought as ht
from hyperthought.metadata import MetadataItem

from . import connect, template  # noqa: F401


class FileSpecificMetadataUniquenessException(Exception):
    pass


class FileStatus(IntEnum):
    """Enum corresponding to status in FileStatus table."""

    PENDING = 1
    READY = 2
    HASH_MATCHES = 3
    MALWARE_FREE = 4
    UPLOADED = 5
    NOT_READY = 6
    HASH_MISMATCH = 7
    MALWARE_DETECTED = 8
    UPLOAD_ERROR = 9
    UNKNOWN_ERROR = 10
    METADATA_UPDATE_ERROR = 11


class ParserStatus(IntEnum):
    """Enum corresponding to status in ParserStatus table."""

    PENDING = 1
    PARSED = 2
    PARSER_ERROR = 3


class TargetRule(IntEnum):
    """
    Enum corresponding to relationships between Rule sources and targets.

    A source is a file from which metadata will be parsed.
    A target is a file or folder to which metadata will be applied.

    These values correspond to the ids in the TargetRule lookup table.
    """
    SELF = 1
    ALL = 2
    PARENT = 3
    PARENT_PROGENY = 4
    SIBLINGS = 5


class FileFilter(Enum):
    """
    Enum used to filter results when getting metadata application records.
    """

    FILES_ONLY = 1
    FOLDERS_ONLY = 2
    ALL = 3


class Database:
    """
    Manager class for a Manifest database.

    Parameters
    ----------
    connection : sqlite3.Connection
        A connection to the database of interest.

    Exceptions
    ----------
    A ValueError will be thrown if the db_connection parameter cannot be
    validated.
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        if not isinstance(connection, sqlite3.Connection):
            raise ValueError("db_connection must be a sqlite3 connection")

        self._connection = connection

    @property
    def connection(self) -> Connection:
        return self._connection

    def create_job_data(
        self,
        job_name: str,
        username: str,
        workspace_alias: str,
        ignore_path: Optional[str] = None,
        hyperthought_root: str = "/",
        avoid_duplicates: bool = False,
        commit: bool = True,
    ) -> None:
        """
        Create a record in the JobData table.

        By assumption, there should only be one such record.
        """
        sql = """
        INSERT INTO JobData (
            job_name,
            username,
            workspace_alias,
            ignore_path,
            hyperthought_root,
            avoid_duplicates
        ) VALUES (
            :job_name,
            :username,
            :workspace_alias,
            :ignore_path,
            :hyperthought_root,
            :avoid_duplicates
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(
            sql,
            {
                "job_name": job_name,
                "username": username,
                "workspace_alias": workspace_alias,
                "ignore_path": ignore_path,
                "hyperthought_root": hyperthought_root,
                "avoid_duplicates": avoid_duplicates,
            },
        )

        if commit:
            self.connection.commit()

    def create_file(
        self,
        name: str,
        is_folder: bool,
        hyperthought_id_path: str,
        hyperthought_id: Optional[str] = None,
        path: Optional[str] = None,
        end_bytes: Optional[List[int]] = None,
        size: Optional[int] = None,
        file_hash: Optional[str] = None,
        commit: bool = True,
    ) -> Optional[int]:
        """
        Create a file record in the database.

        Parameters
        ----------
        name : str
            Name of file or folder.
        is_folder : bool
            True iff the record in question is for a folder, not a file.
        hyperthought_id : str
            The id of the file/folder in HyperThought.  Specified prior to
            document creation.
        hyperthought_id_path : str
            Comma-separated list of parent folder ids in HyperThought.
            Corresponds to content.path in NoSQL database documents.
        path : str or None
            Local path to a file.  Not used for folders.
        end_bytes : list of int
            Comma-separated ints representing bytes found at the end of a file.
        size : int or None
            The expected size of the file.  Required of files, not folders.
        file_hash : str or None
            The hash for the file.  Required of files, not folders.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.

        Returns
        -------
        The id for the file.

        Exceptions
        ----------
        -   ValueErrors will be thrown if the parameters cannot be validated.
        -   An IntegrityError will be thrown if the insert query violates
            integrity constraints.  (This may happen if a record already exists
            for the path, due to a uniqueness constraint.)
        """
        if not is_folder and (not isinstance(size, int) or size < 0):
            raise ValueError("size for a file must be a non-negative integer")

        if is_folder and hyperthought_id is None:
            raise ValueError("A folder must have a 'hyperthought_id'.")

        if end_bytes is not None and not isinstance(end_bytes, str):
            raise ValueError("end_bytes must be a string if provided")

        if end_bytes is not None:
            valid_chars = set("0123456789,")
            invalid_chars = set(end_bytes) - valid_chars

            if invalid_chars:
                raise ValueError(
                    f"Invalid chars in end_bytes: {invalid_chars}")

        # Define and execute the relevant SQL statement.
        sql = """
        INSERT INTO File (
            name,
            hyperthought_id,
            hyperthought_id_path,
            is_folder,
            path,
            end_bytes,
            size,
            file_hash
        )
        VALUES (
            :name,
            :hyperthought_id,
            :hyperthought_id_path,
            :is_folder,
            :path,
            :end_bytes,
            :size,
            :file_hash
        )
        """
        cursor = self.connection.cursor()

        cursor.execute(
            sql,
            {
                "name": name,
                "hyperthought_id": hyperthought_id,
                "hyperthought_id_path": hyperthought_id_path,
                "is_folder": is_folder,
                "path": path,
                "end_bytes": end_bytes,
                "size": size,
                "file_hash": file_hash,
            },
        )
        file_id = cursor.lastrowid

        if commit:
            self.connection.commit()

        return file_id

    def delete_file(self, file_id: int, commit: bool = True) -> None:
        """
        Remove a file record from the database.

        Parameters
        ----------
        file_id : int
            The id of the file to be deleted.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()
        sql = "DELETE FROM File WHERE id = :id"
        cursor.execute(sql, {"id": file_id})

        if commit:
            self.connection.commit()

        cursor.close()

    def delete_files(
        self,
        file_ids: Iterable[int],
        commit: bool = True,
    ) -> None:
        """
        Remove multiple file records from the database.

        Parameters
        ----------
        file_ids : int
            The id of the file to be deleted.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()
        sql_where_in = ", ".join(str(file_id) for file_id in file_ids)
        sql = f"DELETE FROM File WHERE id IN {sql_where_in}"
        cursor.execute(sql)

        if commit:
            self.connection.commit()

        cursor.close()

    def get_total_size(self) -> int:
        """Get the sum of file sizes for all files in the manifest."""
        sql = """
        SELECT SUM(size) AS total_bytes
        FROM File
        WHERE size IS NOT NULL
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row["total_bytes"]

    def create_parser(
        self,
        parser_class: str,
        file_id: int,
        metadata_id: int,
        commit: bool = True,
    ) -> Optional[int]:
        """
        Create a Parser record.

        A Parser record associates a parser class (class name) with a file
        to be parsed.

        Parameters
        ----------
        parser_class : str
            The name of a parser class, as defined in the hyperthought package.
        file_id : int
            id of a File record for the file to be parsed.
        metadata_id : int
            id of the Metadata record that will store the parsed metadata.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.

        Returns
        -------
        The id for the parser.

        Exceptions
        ----------
        -   ValueErrors will be thrown if the parameters cannot be validated.
        -   An IntegrityError will be thrown if the insert query violates
            integrity constraints.  (This may happen if a record already exists
            for a parser/file combination, due to a uniqueness constraint.)
        """
        if parser_class not in ht.parsers.PARSERS:
            raise ValueError(f"'{parser_class}' is not a valid parser class")

        sql = """
        INSERT INTO Parser (file_id, parser_class, metadata_id)
        VALUES (:file_id, :parser_class, :metadata_id)
        """
        cursor = self.connection.cursor()
        cursor.execute(
            sql,
            {
                "file_id": file_id,
                "parser_class": parser_class,
                "metadata_id": metadata_id,
            },
        )
        parser_id = cursor.lastrowid

        if commit:
            self.connection.commit()

        cursor.close()
        return parser_id

    def create_metadata(
        self,
        file_id: int,
        metadata: Optional[List[MetadataItem]] = None,
        commit: bool = True,
    ) -> int:
        """
        Create a Metadata record.

        Store metadata, whether specified directly or parsed from a file,
        in a Metadata table record.

        Parameters
        ----------
        file_id : int
            The file associated with the metadata.
            This will either be the file from which the metadata is parsed,
            or the main file associated with file-specific metadata.
        metadata : list of hyperthought.metadata.MetadataItem or None
            A list of metadata items, in hyperthought package object format.
            The metadata will be converted to the API format before being
            stored in the table, since the METADATA type added to the database
            uses JSON serialization.
            If None, the metadata will be added later when a file is parsed.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.

        Returns
        -------
        The id of the Metadata record created.

        Exceptions
        ----------
        A ValueError will be thrown if the metadata is not valid.
        """
        if metadata is None:
            api_metadata = None
        else:
            if not isinstance(metadata, list):
                raise ValueError("metadata must be a list if not None")

            for item in metadata:
                if not isinstance(item, ht.metadata.MetadataItem):
                    raise ValueError(
                        "all metadata items must be instances of MetadataItem"
                    )

            api_metadata = ht.metadata.to_api_format(metadata=metadata)

        sql = """
        INSERT INTO Metadata (file_id, metadata)
        VALUES (:file_id, :metadata)
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"file_id": file_id, "metadata": api_metadata})
        metadata_id = cursor.lastrowid

        if commit:
            self.connection.commit()

        return metadata_id

    def create_or_update_common_metadata(
        self,
        metadata: List[MetadataItem],
        commit: bool = True,
    ) -> None:
        """
        Add a row to the common metadata table.

        Parameters
        ----------
        metadata : list of hyperthought.metadata.MetadataItem
            Metadata to be added as common metadata.
        """
        if not metadata:
            return

        if not isinstance(metadata, list):
            raise ValueError("metadata must be a list if not None")

        for item in metadata:
            if not isinstance(item, ht.metadata.MetadataItem):
                raise ValueError(
                    "all metadata items must be instances of MetadataItem")

        api_metadata = ht.metadata.to_api_format(metadata=metadata)
        cursor = self.connection.cursor()

        # Remove previously created common metadata, if any.
        sql = "DELETE FROM CommonMetadata"
        cursor.execute(sql)

        # Add common metadata.
        sql = "INSERT INTO CommonMetadata (metadata) VALUES (:metadata)"
        cursor.execute(sql, {"metadata": api_metadata})

        if commit:
            self.connection.commit()

    def create_metadata_application(
        self,
        metadata_id: int,
        file_id: int,
        commit: bool = True,
    ) -> Optional[int]:
        """
        Create a MetadataApplication record to associate metadata with a file.

        Parameters
        ----------
        metadata_id : int
            The id of a record in the Metadata table.
        file_id : int
            The id of a file to which the metadata should be added.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.

        Returns
        -------
        The id of the MetadataApplication record.

        Exceptions
        ----------
        -   An IntegrityError will be thrown if the insert query violates
            integrity constraints.  (This may happen if a record already exists
            for the metadata/file combination, due to a uniqueness constraint.)
        """
        sql = """
        INSERT INTO MetadataApplication (metadata_id, file_id)
        VALUES (:metadata_id, :file_id)
        """
        cursor = self.connection.cursor()
        cursor.execute(
            sql,
            {
                "metadata_id": metadata_id,
                "file_id": file_id,
            },
        )
        metadata_application_id = cursor.lastrowid

        if commit:
            self.connection.commit()

        return metadata_application_id

    def get_job_data(self) -> Optional[Dict]:
        """Get job data from the JobData table."""
        cursor = self.connection.cursor()
        sql = "SELECT * FROM JobData"
        cursor.execute(sql)
        row = cursor.fetchone()

        if row is None:
            return None

        return {key: row[key] for key in row.keys()}

    def get_common_metadata(self) -> List[Dict]:
        """Get common metadata."""
        cursor = self.connection.cursor()
        sql = "SELECT metadata FROM CommonMetadata"
        cursor.execute(sql)
        row = cursor.fetchone()

        if row is None:
            return []

        return row["metadata"]

    def get_parser_count(self) -> int:
        """
        Count the number of Parser records.

        This is also the number of parsing operations.
        """
        cursor = self.connection.cursor()
        sql = "SELECT COUNT(*) AS parser_count FROM Parser"
        cursor.execute(sql)
        return cursor.fetchone()["parser_count"]

    def get_parsers_for_file(
        self,
        file_id: int
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
        cursor = self.connection.cursor()
        sql = "SELECT * FROM Parser WHERE file_id = :file_id"
        cursor.execute(sql, {"file_id": file_id})

        for row in cursor.fetchall():
            yield{
                key: row[key]
                for key in row.keys()
            }

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
        sql = "SELECT * FROM File"

        if filter_ == FileFilter.FILES_ONLY:
            sql += " WHERE NOT is_folder"
        elif filter_ == FileFilter.FOLDERS_ONLY:
            sql += " WHERE is_folder"

        cursor = self.connection.cursor()
        cursor.execute(sql)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

        cursor.close()

    def get_file_id(self, path: str) -> Optional[int]:
        """Get an id for a File record given a path."""
        cursor = self.connection.cursor()
        sql = """
        SELECT id
        FROM File
        WHERE path = :path
        """
        cursor.execute(sql, {"path": path})
        row = cursor.fetchone()

        if row is None:
            return None

        cursor.close()
        return row["id"]

    def get_file_ids(self, paths: Iterable[str]) -> List[int]:
        """Get a list of file ids for given paths."""
        cursor = self.connection.cursor()

        def quote(s):
            return f'"{s}"'

        sql = f"""
        SELECT id
        FROM File
        WHERE path IN ({", ".join(quote(path) for path in paths)})
        """

        cursor.execute(sql)

        file_ids = [
            row["id"]
            for row in cursor.fetchall()
        ]

        cursor.close()
        return file_ids

    def get_all_file_metadata(self, file_id: int) -> List[Dict]:
        """
        Get all metadata to be added to a file in HyperThought.

        Get all metadata using MetadataApplication records as a lookup for
        Metadata records.

        Parameters
        ----------
        file_id : int
            The database id for the file of interest.

        Returns
        -------
        Aggregated API-formatted metadata from all sources.
        """
        all_metadata = []
        sql = """
            SELECT metadata FROM CommonMetadata
            UNION
            SELECT metadata
            FROM MetadataApplication INNER JOIN Metadata
                ON MetadataApplication.metadata_id = Metadata.id
            WHERE MetadataApplication.file_id = :file_id
            """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"file_id": file_id})

        for row in cursor.fetchall():
            metadata = row["metadata"]

            if metadata:
                all_metadata.extend(row["metadata"])

        return all_metadata

    def get_file(
        self,
        file_id: Optional[int] = None,
        name: Optional[str] = None,
        hyperthought_id_path: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get a file/folder record given identifying information.

        Parameters
        ----------
        file_id : int or None
            The database id for the file/folder.
        name: str or None
            The name of the file/folder.
        hyperthought_id_path: str or None
            Comma-separated parent folder ids, e.g. ",uuid,uuid,uuid,".

        Either file_id or name and hyperthought_id must be provided.
        """
        if file_id is None and (name is None or hyperthought_id_path) is None:
            raise ValueError(
                "file_id or name and hyperthought_id_path must be provided")

        cursor = self.connection.cursor()

        if file_id:
            sql = "SELECT * FROM File WHERE id = :file_id"
            cursor.execute(sql, {"file_id": file_id})
        else:
            sql = """
            SELECT *
            FROM File
            WHERE
                name = :name
                AND
                hyperthought_id_path = :hyperthought_id_path
            """
            cursor.execute(sql, {
                "name": name,
                "hyperthought_id_path": hyperthought_id_path,
            })

        row = cursor.fetchone()

        if not row:
            return None

        return {key: row[key] for key in row.keys()}

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

        Yields
        -------
        Dicts containing file record data.
        """
        if not file_ids and not paths:
            raise ValueError("file_ids or paths must be provided")

        if file_ids:
            sql = "SELECT * FROM File WHERE id IN ("
            items = file_ids
        else:
            sql = "SELECT * FROM File WHERE path IN ("
            # TODO:  Resolve or ignore mypy issue.
            items = paths

        params = {}
        key_index = 0

        for item in items:
            key = f"item_{key_index}"
            key_index += 1
            sql += f":{key}, "
            params[key] = item

        sql = sql[:-2] + ")"  # Remove trailing ", " and close parenthesis.
        cursor = self.connection.cursor()
        cursor.execute(sql, params)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

        cursor.close()

    def get_all_metadata_application(
        self
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """Get all MetadataApplication records."""
        cursor = self.connection.cursor()
        sql = """
        SELECT
            MetadataApplication.*,
            File.hyperthought_id
        FROM
            MetadataApplication INNER JOIN File
                ON MetadataApplication.file_id = File.id
        """
        cursor.execute(sql)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

    def get_all_parsers(
        self
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """Get all Parser records."""
        cursor = self.connection.cursor()
        sql = """
        SELECT
            Parser.*,
            File.hyperthought_id
        FROM
            Parser INNER JOIN File
                ON Parser.file_id = File.id
        """
        cursor.execute(sql)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

    def get_parser_counts_for_files(
        self,
        file_ids: List[int],
    ) -> Dict[int, int]:
        """
        Get parser counts for given files.

        Parameters
        ----------
        file_id : list of int
            File ids of interest.

        Returns
        -------
        A dict mapping each file id to the number of parsers associated with
        the file.
        """
        for file_id in file_ids:
            if not isinstance(file_id, int):
                raise ValueError(f"{file_id} is not an int")

        file_list = ", ".join(str(file_id) for file_id in file_ids)
        sql = f"""
        SELECT
            File.id AS file_id,
            COUNT(*) AS parser_count
        FROM
            File INNER JOIN Parser ON File.id = Parser.file_id
        WHERE
            File.id IN ({file_list})
        GROUP BY
            File.id
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        results = {
            row["file_id"]: row["parser_count"]
            for row in cursor.fetchall()
        }
        cursor.close()
        return results

    def get_all_metadata(
        self,
        file_specific: bool = True
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Get all Metadata records.

        Parameters
        ----------
        file_specific : bool
            If true, filter results to include only those records with
            no corresponding Parser record.
        """
        cursor = self.connection.cursor()

        if file_specific:
            sql = """
            SELECT Metadata.*
            FROM Metadata LEFT JOIN Parser
                ON Metadata.id = Parser.metadata_id
            WHERE Parser.id IS NULL
            """
        else:
            sql = "SELECT * FROM Metadata"

        cursor.execute(sql)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

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

        sql_params = {}

        if file_id:
            sql = """
            SELECT
                Rule.*
            FROM
                Rule
                INNER JOIN RuleParser ON Rule.id = RuleParser.rule_id
                INNER JOIN Parser on RuleParser.parser_id = Parser.id
            WHERE
                Parser.file_id = :file_id
            """
            sql_params["file_id"] = file_id

            if parser:
                # TODO:  Resolve or ignore mypy issue.
                sql += """
                AND
                Parser.parser_class = :parser
                """
                sql_params["parser"] = parser
        else:
            sql = "SELECT * FROM Rule"

            if parser:
                # TODO:  Resolve or ignore mypy issue.
                sql += " WHERE parser_class = :parser"
                sql_params["parser"] = parser

        cursor = self.connection.cursor()
        cursor.execute(sql, sql_params)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

    def _update(
        self,
        table: str,
        id_: int,
        updates: Dict,
        commit: bool = True,
    ) -> None:
        """
        Convenience function used to update a record.

        The caller will be responsible for ensuring that keys in the updates
        dict correspond to attributes in the table.
        """
        valid_tables = (
            "File",
            "Parser",
            "Metadata",
        )

        if table not in valid_tables:
            raise ValueError(f"Invalid table: {table}")

        sql = f"UPDATE {table} "

        set_statements = []
        params = {}

        for key in updates:
            set_statements.append(f"{key} = :{key}")
            params[key] = updates[key]

        sql += "SET " + ",".join(set_statements) + " WHERE id = :id"
        params["id"] = id_

        cursor = self.connection.cursor()
        cursor.execute(sql, params)

        if commit:
            self.connection.commit()

    def update_file(
        self,
        id_: int,
        updates: Dict,
        commit: bool = True,
    ) -> None:
        """
        Update a file record.

        Parameters
        ----------
        id_ : int
            id of the file to be updated.
        updates : dict
            Updates to be committed to the database.
            Keys must correspond to File table attributes.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        self._update(table="File", id_=id_, updates=updates, commit=commit)

    def reset_file_statuses(
        self,
        existing_statuses: List[FileStatus],
        new_status: FileStatus,
        commit: bool = True,
    ) -> None:
        """
        Reset file statuses to a new value.

        All file records having one of the specified existing statuses
        will have their status changed to the new status.

        Parameters
        ----------
        existing_statuses : list of FileStatus
            The file statuses to be changed.
        new_status : FileStatus
            The status to which all file records with one of the existing
            statuses will be changed.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        status_map = {
            f"status{i:02}": existing_statuses[i].value
            for i in range(len(existing_statuses))
        }

        sql = """
            UPDATE File
            SET file_status_id = :new_status_id
            WHERE
                file_status_id IN (
            """

        for key in status_map:
            sql += f":{key}, "

        # Remove comma + space and add closing parenthesis.
        sql = sql[:-2] + ")"

        status_map["new_status_id"] = new_status.value
        cursor = self.connection.cursor()
        cursor.execute(sql, status_map)

        if commit:
            self.connection.commit()

    def get_parser(
        self,
        parser_id: Optional[int] = None,
        file_id: Optional[int] = None,
        parser_class: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get a parser record data given either a parser id or a file_id and
        a parser_class.

        Parameters
        ----------
        parser_id : int or None
            An id for a Parser record.
        file_id : int or None
            An id for a File record.
        parser_class : str or None
            The class name for a parser.

        Either parser_id or both file_id and parser_class must be provided.

        Returns
        -------
        A dict containing data from a Parser record, or None if the search
        could not find a Parser record.
        """
        if parser_id is None and (file_id is None or parser_class is None):
            raise ValueError(
                "Either parser_id or both file_id and parser class must be "
                "provided."
            )

        if parser_id:
            sql = "SELECT * FROM Parser WHERE id = :parser_id"
            params = {"parser_id": parser_id}
        else:
            sql = """
            SELECT *
            FROM Parser
            WHERE
                file_id = :file_id
                AND
                parser_class = :parser_class
            """
            # TODO:  Resolve or ignore mypy issue.
            params = {
                "file_id": file_id,
                "parser_class": parser_class,
            }

        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()

        if not row:
            return None

        return {key: row[key] for key in row.keys()}

    def get_progeny(
        self,
        folder_path: str
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """Get all children of a given folder that are in the manifest."""
        cursor = self.connection.cursor()
        sql = "SELECT * FROM File WHERE path LIKE :path_pattern"
        path_pattern = f"{folder_path.rstrip(os.path.sep)}{os.path.sep}%"
        cursor.execute(sql, {"path_pattern": path_pattern})

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

        cursor.close()

    def update_parser(
        self,
        id_: int,
        updates: Dict,
        commit: bool = True,
    ) -> None:
        """
        Update a parser record.

        Parameters
        ----------
        id_ : int
            id of the parser to be updated.
        updates : dict
            Updates to be committed to the database.
            Keys must correspond to Parser table attributes.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        self._update(table="Parser", id_=id_, updates=updates, commit=commit)

    def get_metadata(self, metadata_id: int) -> Optional[Dict]:
        """Get a metadata record from a metadata id."""
        sql = "SELECT * FROM Metadata WHERE id = :metadata_id"
        cursor = self.connection.cursor()
        cursor.execute(sql, {"metadata_id": metadata_id})
        row = cursor.fetchone()

        if not row:
            return None

        return {key: row[key] for key in row.keys()}

    def update_metadata(
        self,
        id_: int,
        updates: Dict,
        commit: bool = True,
    ) -> None:
        """
        Update a metadata record.

        Parameters
        ----------
        id_ : int
            id of the metadata record to be updated.
        updates : dict
            Updates to be committed to the database.
            Keys must correspond to Metadata table attributes.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        self._update(table="Metadata", id_=id_, updates=updates, commit=commit)

    def bulk_load_files(
        self,
        file_data: List[Dict],
        commit: bool = True,
    ) -> None:
        """
        Bulk load files in the database.

        Parameters
        ----------
        file_data : list of dicts
            Data on the files to be loaded.
            Keys in each dict must include the following:
                name : str
                    The name of the file or folder.
                hyperthought_id_path : str
                    Comma-separated list of parent folder ids in HyperThought.
                    Corresponds to content.path in NoSQL database documents.
                is_folder : bool
                    True iff the record in question is for a folder,
                    not a file.
                path : str
                    Local path to the file or folder.
                    Can be None (for folders that don't exist locally).
                end_bytes : str or None
                    Comma-separated ints representing bytes found at the end
                    of a file.
                size : int or None
                    The expected size of the file.
                    Required of files, not folders.
                file_hash : str or None
                    The hash for the file.  Required of files, not folders.
            Data for folders must include the following:
                hyperthought_id : str
                    The id of the folder in HyperThought.
                    (Specified prior to document creation.)
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()
        next_id = self.get_last_id(table="File") + 1
        required_keys = {
            "name",
            "hyperthought_id_path",
            "is_folder",
            "path",
            "end_bytes",
            "size",
            "file_hash",
        }

        for item in file_data:
            if not isinstance(item, dict):
                raise ValueError("All elements of file_data must be dicts.")

            keys = set(item.keys())
            missing_keys = required_keys - keys

            if missing_keys:
                raise ValueError(
                    f"Element in file_data missing keys: {missing_keys}")

            if item["is_folder"] and "hyperthought_id" not in keys:
                raise ValueError(
                    "Folder element in file_data missing key "
                    "'hyperthought_id'.")

            item["id"] = next_id
            next_id += 1

        sql = """
            INSERT INTO File (
                name,
                hyperthought_id,
                hyperthought_id_path,
                is_folder,
                path,
                end_bytes,
                size,
                file_hash
            ) VALUES (
                :name,
                :hyperthought_id,
                :hyperthought_id_path,
                :is_folder,
                :path,
                :end_bytes,
                :size,
                :file_hash
            )
            """
        cursor.executemany(sql, file_data)

        if commit:
            self.connection.commit()

    def bulk_load_parsers(
        self,
        parser_data: List[Dict],
        commit: bool = True,
    ) -> None:
        """
        Bulk load parsers into the database. Will add a database_id in place to
        parser_data entries.

        ids for the parsers will be added to parser_data in place.

        Parameters
        ----------
        parser_data : list of dict
            Consists of metadata parsers for files to be uploaded. Each parser
            entry should contain the following keys:
                file_id : int
                    Foreign key id of the file the parser is associated with.
                parser_class : string
                    Class of the parser.
                metadata_id : int
                    Foreign key id of the metadata associated with the parser.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()
        next_id = self.get_last_id(table="Parser") + 1
        required_keys = {
            "file_id",
            "parser_class",
            "metadata_id",
        }

        for item in parser_data:
            if not isinstance(item, dict):
                raise ValueError("All elements of parser_data must be dicts.")

            keys = set(item.keys())
            missing_keys = required_keys - keys

            if missing_keys:
                raise ValueError(
                    f"Element in parser_data missing keys: {missing_keys}")

            item["id"] = next_id
            next_id += 1

        sql = """
            INSERT INTO Parser (
                id,
                file_id,
                parser_class,
                metadata_id
            ) VALUES (
                :id,
                :file_id,
                :parser_class,
                :metadata_id
            )
        """
        cursor.executemany(sql, parser_data)

        if commit:
            self.connection.commit()

    def bulk_load_metadata(
        self,
        metadata_data: List[Dict],
        commit: bool = True,
    ) -> None:
        """
        Bulk load metadata into the database. Will add a database_id in place
        to metadata_data entries.

        ids for the new records will be added to metadata_data in place.

        Parameters
        ----------
        metadata_data : list of dict
            contains metadata entries with the following keys to be committed
            to the database:
                file_id : int
                metadata : list of dicts or None
                    API-formatted metadata
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()
        next_id = self.get_last_id(table="Metadata") + 1
        required_keys = {
            "file_id",
            "metadata",
        }

        for item in metadata_data:
            if not isinstance(item, dict):
                raise ValueError(
                    "All elements of metadata_data must be dicts.")

            keys = set(item.keys())
            missing_keys = required_keys - keys

            if missing_keys:
                raise ValueError(
                    f"Element in metadata_data missing keys: {missing_keys}"
                )

            item["id"] = next_id
            next_id += 1

        sql = """
            INSERT INTO Metadata (
                id,
                file_id,
                metadata
            ) VALUES (
                :id,
                :file_id,
                :metadata
            )
            """
        cursor.executemany(sql, metadata_data)

        if commit:
            self.connection.commit()

    def _filter_metadata_application_data(
        self,
        metadata_application_data: List[Dict],
    ) -> List[Dict]:
        """
        Filter entries corresponding to records that already exist.

        Remove entries from metadata_application_data if a file_id and
        metadata_id have already been associated in the MetadataAppication
        junction table.
        """

        def get_key(item: Dict) -> str:
            """Get a key to track file/metadata association."""
            return f"{item['file_id']}_{item['metadata_id']}"

        ids_to_data = {}
        sql_where = ""
        sql_params = {}
        index = 0

        for item in metadata_application_data:
            # Add item to lookup data structure.
            key = get_key(item)
            ids_to_data[key] = item

            # Add item to SQL.
            index += 1
            file_id_key = f"file_id_{index}"
            metadata_id_key = f"metadata_id_{index}"
            sql_params.update({
                file_id_key: item["file_id"],
                metadata_id_key: item["metadata_id"],
            })
            sql_where += (
                f"OR file_id = :{file_id_key} "
                f"AND metadata_id = :{metadata_id_key} "
            )

        # Trim first "OR " from the WHERE clause.
        sql_where = sql_where[len("OR "):]

        # Find duplicates and remove from lookup data structure.
        sql = f"""
        SELECT file_id, metadata_id
        FROM MetadataApplication
        WHERE {sql_where}
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, sql_params)

        for row in cursor.fetchall():
            key = get_key(row)
            del ids_to_data[key]

        # Return the filtered list.
        return list(ids_to_data.values())

    def bulk_load_metadata_application(
        self,
        metadata_application_data: List[Dict],
        commit: bool = True,
    ) -> None:
        """
        Bulk load MetadataApplication data into the database.

        metadata_application_data entries will have a database_id added to them
        in place.

        ids for the new records will be added to metadata_application_data
        in place.

        Parameters
        ----------
        metadata_application_data : list
            contains MetadataApplication entries with the following keys to be
            committed to the database:
                metadata_id : int
                    id of record in Metadata table.
                file_id : int
                    id of record in File table.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        if not metadata_application_data:
            return

        metadata_application_data = self._filter_metadata_application_data(
            metadata_application_data=metadata_application_data,
        )

        if not metadata_application_data:
            return

        cursor = self.connection.cursor()
        # Create MetadataApplication records.
        next_id = self.get_last_id(table="MetadataApplication") + 1
        required_keys = {
            "metadata_id",
            "file_id",
        }

        for item in metadata_application_data:
            if not isinstance(item, dict):
                raise ValueError(
                    "All elements of metadata_application_data must be dicts."
                )

            keys = set(item.keys())
            missing_keys = required_keys - keys

            if missing_keys:
                raise ValueError(
                    "Element in metadata_application_data missing keys: "
                    f"{missing_keys}"
                )

            item["id"] = next_id
            next_id += 1

        sql = """
            INSERT INTO MetadataApplication (
                id,
                metadata_id,
                file_id
            ) VALUES (
                :id,
                :metadata_id,
                :file_id
            )
        """
        cursor.executemany(sql, metadata_application_data)

        if commit:
            self.connection.commit()

    def bulk_load_rules(
        self,
        rule_data: List[Dict],
        commit: bool = True,
    ) -> None:
        """
        Bulk load Rule data into the database.

        ids for the new records will be added to rule_data in place.

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
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()
        next_id = self.get_last_id(table="Rule") + 1
        required_keys = {
            "source_pattern",
            "parser_class",
            "target_rule_id",
            "target_pattern",
            "name",
        }

        for item in rule_data:
            if not isinstance(item, dict):
                raise ValueError(
                    "All elements of rule_data must be dicts."
                )

            keys = set(item.keys())
            missing_keys = required_keys - keys

            if missing_keys:
                raise ValueError(
                    "Element in metadata_application_data missing keys: "
                    f"{missing_keys}"
                )

            item["id"] = next_id
            next_id += 1

        sql = """
            INSERT INTO Rule (
                id,
                source_pattern,
                parser_class,
                target_rule_id,
                target_pattern,
                name
            ) VALUES (
                :id,
                :source_pattern,
                :parser_class,
                :target_rule_id,
                :target_pattern,
                :name
            )
        """
        cursor.executemany(sql, rule_data)

        if commit:
            self.connection.commit()

    def update_file_status(
        self,
        file_ids: Iterable[int],
        status: FileStatus,
        commit: bool = True,
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
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        file_ids = list(file_ids)

        for file_id in file_ids:
            if not isinstance(file_id, int):
                raise ValueError("All file ids must be ints.")

        file_ids_in = ", ".join(str(file_id) for file_id in file_ids)
        sql = f"""
        UPDATE File
        SET file_status_id = :file_status_id
        WHERE id IN ({file_ids_in})
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"file_status_id": status.value})

        if commit:
            self.connection.commit()

        cursor.close()

    def get_last_id(self, table: str) -> int:
        """Get the last id in a table."""
        valid_tables = {
            "Parser",
            "Metadata",
            "MetadataApplication",
            "File",
            "Rule",
        }

        if table not in valid_tables:
            raise ValueError(f"Invalid table: {table}")

        sql = f"SELECT MAX(id) AS last_id FROM {table}"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        last_id = result["last_id"]

        if last_id is None:
            last_id = 0

        return last_id

    def get_file_count(self, include_root_folders: bool = False) -> int:
        """Get number of files in the database."""
        cursor = self.connection.cursor()

        if include_root_folders:
            sql = "SELECT COUNT(*) AS file_count FROM File"
        else:
            # As of 2/15/2023, a File record corresponds to a HyperThought
            # root folder iff its path is null.
            sql = """
            SELECT COUNT(*) AS file_count
            FROM File
            WHERE path IS NOT NULL
            """

        cursor.execute(sql)
        result = cursor.fetchone()
        return result["file_count"]

    def update_folder_hyperthought_id(
        self,
        old_id: str,
        new_id: str,
        commit: bool = True,
    ) -> None:
        """
        Update database when an existing folder is found in HyperThought.

        Change the id of the folder record, as well as id paths for all
        progeny.

        Parameters
        ----------
        old_id : str
            The id of the folder according to the database.
        new_id : str
            The id of the folder in HyperThought.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.
        """
        cursor = self.connection.cursor()

        # Get the folder record.
        sql = "SELECT * FROM File WHERE hyperthought_id = :old_id"
        cursor.execute(sql, {"old_id": old_id})
        folder = cursor.fetchone()

        if not folder:
            return

        # Reset id for folder record.
        updates = {"hyperthought_id": new_id}
        self.update_file(id_=folder["id"], updates=updates, commit=commit)

        # Reset id paths for progeny.
        parent_path = folder["hyperthought_id_path"]
        old_id_path = f"{parent_path}{old_id},"
        new_id_path = f"{parent_path}{new_id},"
        sql = """
        UPDATE File
        SET hyperthought_id_path = REPLACE(
            hyperthought_id_path, :old_id_path, :new_id_path)
        WHERE hyperthought_id_path LIKE :pattern
        """
        cursor.execute(sql, {
            "old_id_path": old_id_path,
            "new_id_path": new_id_path,
            "pattern": f"{old_id_path}%"
        })

        if commit:
            self.connection.commit()

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
            Specify filter for results.

        Yields
        ------
        Ids for files to which metadata will be applied.
        """
        if filter_ == FileFilter.FILES_ONLY:
            sql = """
            SELECT
                MetadataApplication.file_id
            FROM
                Metadata
                INNER JOIN MetadataApplication
                    ON Metadata.id = MetadataApplication.metadata_id
                INNER JOIN File
                    ON MetadataApplication.file_id = File.id
            WHERE
                Metadata.id = :metadata_id
                AND
                NOT File.is_folder
            """
        elif filter_ == FileFilter.FOLDERS_ONLY:
            sql = """
            SELECT
                MetadataApplication.file_id
            FROM
                Metadata
                INNER JOIN MetadataApplication
                    ON Metadata.id = MetadataApplication.metadata_id
                INNER JOIN File
                    ON MetadataApplication.file_id = File.id
            WHERE
                Metadata.id = :metadata_id
                AND
                File.is_folder
            """
        else:
            sql = """
            SELECT
                MetadataApplication.file_id
            FROM
                Metadata
                INNER JOIN MetadataApplication
                    ON Metadata.id = MetadataApplication.metadata_id
            WHERE
                Metadata.id = :metadata_id
            """

        cursor = self._connection.cursor()
        cursor.execute(sql, {"metadata_id": metadata_id})

        for row in cursor.fetchall():
            yield row["file_id"]

        cursor.close()

    def has_connectivity_errors(self) -> bool:
        """Determine whether connectivity errors occurred."""
        sql = """
        SELECT COUNT(*) AS error_count
        FROM File
        WHERE file_status_id IN (
            :upload_error_status_id,
            :metadata_update_error_status_id
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(
            sql,
            {
                "upload_error_status_id": FileStatus.UPLOAD_ERROR.value,
                "metadata_update_error_status_id": (
                    FileStatus.METADATA_UPDATE_ERROR.value),
            },
        )
        row = cursor.fetchone()
        return bool(row["error_count"])

    def has_other_errors(self) -> bool:
        """Determine whether any non-connectivity errors occurred."""
        sql = """
        SELECT COUNT(*) AS error_count
        FROM File
        WHERE file_status_id IN (
            :hash_mismatch_status_id,
            :malware_detected_status_id,
            :other_error_status_id
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(
            sql,
            {
                "hash_mismatch_status_id": FileStatus.HASH_MISMATCH.value,
                "malware_detected_status_id": (
                    FileStatus.MALWARE_DETECTED.value),
                "other_error_status_id": FileStatus.UNKNOWN_ERROR.value,
            },
        )
        row = cursor.fetchone()
        return bool(row["error_count"])

    def create_rule(
        self,
        source_pattern: str,
        parser_class: str,
        target_rule_id: int,
        target_pattern: Optional[str] = None,
        name: Optional[str] = None,
        commit: bool = True,
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
        target_rule_id : int
            id for lookup record specifying relationship between source file
            and target files/folders.
        target_pattern : str
            A pattern which a target file/folder must satisfy in order for the
            extracted metadata to be applied.
        name : str
            A name for a rule to be displayed in the UI.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.

        Patterns must work with the SQL LIKE operator.
        For example, the '%' character will match any number of characters.

        Returns
        -------
        The id of the last row created.
        """
        cursor = self.connection.cursor()
        sql = """
        INSERT INTO Rule (
            source_pattern,
            parser_class,
            target_rule_id,
            target_pattern,
            name
        ) VALUES (
            :source_pattern,
            :parser_class,
            :target_rule_id,
            :target_pattern,
            :name
        )
        """
        cursor.execute(sql, {
            "source_pattern": source_pattern,
            "parser_class": parser_class,
            "target_rule_id": target_rule_id,
            "target_pattern": target_pattern,
            "name": name,
        })
        rule_id = cursor.lastrowid

        if commit:
            self.connection.commit()

        return rule_id

    def get_rule_matches_for_file_as_target(
        self,
        path: str
    ) -> Generator[int, Optional[None], Optional[None]]:
        """
        Find rules a file matches as a target.

        A target file is a file to which metadata will be applied.

        Parameters
        ----------
        path : str
            A file path.

        Yields
        ------
        metadata ids for metadata to be applied to the file.
        """
        sql_statements = []
        sql_params = []
        sql_start = """
        SELECT
            Parser.metadata_id
        FROM
            Rule
            INNER JOIN RuleParser ON Rule.id = RuleParser.rule_id
            INNER JOIN Parser ON RuleParser.parser_id = Parser.id
            INNER JOIN File ON Parser.file_id = File.id
        WHERE
        """
        # The left and right sides of the LIKE operator are inverted
        # (i.e., value LIKE column rather than column LIKE value) on purpose.
        sql_end = """
            AND
            (
                Rule.target_pattern IS NULL
                OR
                :path LIKE Rule.target_pattern
            )
        """

        # self
        sql_self = """
            Rule.target_rule_id = :self_target_rule_id
            AND
            File.path = :path
        """
        sql = sql_start + sql_self + sql_end
        sql_statements.append(sql)
        sql_params.append({
            "path": path,
            "self_target_rule_id": TargetRule.SELF,
        })

        # all
        sql_all = """
            Rule.target_rule_id = :all_target_rule_id
        """
        sql = sql_start + sql_all + sql_end
        sql_statements.append(sql)
        sql_params.append({
            "path": path,
            "all_target_rule_id": TargetRule.ALL,
        })

        # parent
        sql_parent = """
            Rule.target_rule_id = :parent_target_rule_id
            AND
            IsParent(File.path, :path)
        """
        sql = sql_start + sql_parent + sql_end
        sql_statements.append(sql)
        sql_params.append({
            "path": path,
            "parent_target_rule_id": TargetRule.PARENT,
        })

        # parent progeny
        sql_parent_progeny = """
            Rule.target_rule_id = :parent_progeny_target_rule_id
            AND
            IsParentProgeny(File.path, :path)
        """
        sql = sql_start + sql_parent_progeny + sql_end
        sql_statements.append(sql)
        sql_params.append({
            "path": path,
            "parent_progeny_target_rule_id": TargetRule.PARENT_PROGENY,
        })

        # siblings
        sql_siblings = """
            Rule.target_rule_id = :siblings_target_rule_id
            AND
            IsSibling(File.path, :path)
        """
        sql = sql_start + sql_siblings + sql_end
        sql_statements.append(sql)
        sql_params.append({
            "path": path,
            "siblings_target_rule_id": TargetRule.SIBLINGS,
        })

        # Run SQL statements and yield metadata ids.
        cursor = self.connection.cursor()

        for sql, params in zip(sql_statements, sql_params):
            cursor.execute(sql, params)

            for row in cursor.fetchall():
                yield row["metadata_id"]

        cursor.close()

    def get_rule_matches_for_file_as_source(
        self,
        path: str
    ) -> Generator[Dict, Optional[None], Optional[None]]:
        """
        Find rules for which a file matches as a parser source.

        A source file is a file from which metadata will be extracted.

        Parameters
        ----------
        path : str
            A file path.

        Yields
        ------
        All Rule records where the source path matches Rule.source_pattern.
        """
        # Find matching rules.
        # The left and right sides of the LIKE operator are inverted
        # (i.e., value LIKE column rather than column LIKE value) on purpose.
        sql = """
        SELECT *
        FROM Rule
        WHERE :path LIKE source_pattern
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"path": path})

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

        cursor.close()

    def create_rule_parser(
        self,
        rule_id: int,
        parser_id: int,
        commit: bool = True,
    ) -> int:
        """
        Create a RuleParser record.

        Parameters
        ----------
        rule_id : int
            id for a Rule record.
        parser_id : int
            id for a Parser record.
        commit : bool
            Determines whether changes will be committed to the database.
            This may be false if the changes are part of a transaction.

        Returns
        -------
        The id of the last row created.
        """
        sql = """
        INSERT INTO RuleParser (rule_id, parser_id)
        VALUES (:rule_id, :parser_id)
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"rule_id": rule_id, "parser_id": parser_id})
        rule_parser_id = cursor.lastrowid

        if commit:
            self.connection.commit()

        return rule_parser_id

    def create_metadata_for_rule_match(self, file_id: int, rule: Dict) -> int:
        """
        Create records when a file matches a rule as a metadata source.

        Parser, Metadata, and RuleParser records will be created as needed.

        This function will not verify that the file matches a rule.
        See .get_source_matches to get rules that match the file.

        Parameters
        ----------
        file_id : int
            The id of the file in question.
        rule : dict
            A dictionary containing data from a Rule record.

        Returns
        -------
        The id of the RuleParser record that associates the Rule with the
        File, Parser, and Metadata records.
        """
        parser_class = rule["parser_class"]

        # Create Metadata and Parser records as needed.
        parser = self.get_parser(file_id=file_id, parser_class=parser_class)

        if not parser:
            metadata_id = self.create_metadata(file_id=file_id)
            parser_id = self.create_parser(
                file_id=file_id,
                parser_class=parser_class,
                metadata_id=metadata_id,
            )
        else:
            parser_id = parser["id"]
            metadata_id = parser["metadata_id"]

        # Create a RuleParser record.
        # TODO:  Resolve or ignore mypy issue.
        self.create_rule_parser(
            rule_id=rule["id"],
            parser_id=parser_id,
        )

        return metadata_id

    def get_files_matching_rule_as_target(
        self,
        source_path: str,
        rule: Dict,
    ) -> Generator[int, Optional[None], Optional[None]]:
        """
        Find files to which new metadata should be applied.

        Parameters
        ----------
        source_path : str
            The source path of a file matching a given rule.
        rule : dict
            A Rule record.

        Yields
        ------
        File ids for files that match as rule targets.
        """
        target_rule_id = rule["target_rule_id"]
        sql_base = "SELECT id AS file_id FROM File "
        sql_where = ""
        sql_params = {}

        if rule["target_pattern"]:
            sql_where = "WHERE path LIKE :target_pattern "
            sql_params["target_pattern"] = rule["target_pattern"]

        and_ = "AND " if sql_where else "WHERE "

        if target_rule_id == TargetRule.SELF:
            sql_where += and_ + "path = :source_path"
            sql_params["source_path"] = source_path
        elif target_rule_id == TargetRule.ALL:
            # No SQL changes needed.
            pass
        elif target_rule_id == TargetRule.PARENT:
            sql_where += and_ + "IsParent(path, :source_path)"
            sql_params["source_path"] = source_path
        elif target_rule_id == TargetRule.PARENT_PROGENY:
            sql_where += and_ + "IsParentProgeny(path, :source_path)"
            sql_params["source_path"] = source_path
        elif target_rule_id == TargetRule.SIBLINGS:
            sql_where += and_ + "IsSibling(path, :source_path)"
            sql_params["source_path"] = source_path
        else:
            raise ValueError(f"Invalid target_rule_id: {target_rule_id}")

        sql = sql_base + sql_where
        cursor = self.connection.cursor()
        cursor.execute(sql, sql_params)

        for row in cursor.fetchall():
            yield row["file_id"]

        cursor.close()

    def get_target_rules(self) -> List[Dict]:
        """Get all target rule options."""
        cursor = self.connection.cursor()
        sql = "SELECT * FROM TargetRule"
        cursor.execute(sql)

        target_rules = [
            {
                key: row[key]
                for key in row.keys()
            }
            for row in cursor.fetchall()
        ]

        cursor.close()
        return target_rules

    def get_file_page(self, start: int, length: int) -> List[Dict]:
        """
        Get a single page of file results.

        Parameters
        ----------
        start : int
            The start index for the page.
        length : int
            The page length.

        Indexing is effectively zero-based.

        Returns
        -------
        List of dicts containing file information.
        """
        # Start by getting results of interest from the database.
        sql = """
        SELECT
            File.id,
            File.path,
            File.size,
            FileStatus.status,
            File.is_folder
        FROM
            File
            INNER JOIN FileStatus ON File.file_status_id = FileStatus.id
        WHERE
            File.path IS NOT NULL
        ORDER BY
            File.path
        LIMIT
            :start, :length
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {
            "start": start,
            "length": length,
        })
        file_records = [
            {
                key: row[key]
                for key in row.keys()
            }
            for row in cursor.fetchall()
        ]
        cursor.close()

        # Next, transform the records so they contain data needed for the files
        # list view.
        # TODO:  Resolve or ignore mypy issue.
        job_data = self.get_job_data()
        # TODO:  Resolve or ignore mypy issue.
        ignore_path = job_data["ignore_path"]
        len_ignore_path = len(ignore_path)
        hyperthought_root = job_data["hyperthought_root"].rstrip("/")

        def get_hyperthought_path(file_record: Dict) -> str:
            relative_path = (
                file_record["path"][len_ignore_path:]
                .replace("\\", "/")
                .lstrip("/")
            )
            return f"{hyperthought_root}/{relative_path}"

        def get_type(file_record: Dict) -> str:
            if file_record["is_folder"]:
                return "Folder"

            extension = os.path.splitext(file_record["path"])[-1].strip(".")
            return extension

        def transform_record(file_record: Dict) -> Dict:
            return {
                "id": file_record["id"],
                "local_path": file_record["path"],
                "hyperthought_path": get_hyperthought_path(file_record),
                "type": get_type(file_record),
                "size": file_record["size"],
                "status": file_record["status"],
            }

        file_page = [
            transform_record(file_record)
            for file_record in file_records
        ]

        # Return the result.
        return file_page

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
        sql = """
        SELECT
            Metadata.id AS metadata_id
        FROM
            Metadata
            LEFT JOIN Parser ON Metadata.id = Parser.metadata_id
            WHERE
                Metadata.file_id = :file_id
                AND
                Parser.id IS NULL
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"file_id": file_id})
        row = cursor.fetchone()

        if not row:
            cursor.close()
            return None

        metadata_id = row["metadata_id"]
        row = cursor.fetchone()
        cursor.close()

        if row is not None:
            raise FileSpecificMetadataUniquenessException(
                "Multiple file-specific Metadata records found for file "
                f"with id {file_id}."
            )

        return metadata_id

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
        # Make defensive copy and ensure multiple iteration.
        file_ids = list(file_ids)

        # Validate file_ids.
        for file_id in file_ids:
            if not isinstance(file_id, int):
                raise ValueError("file ids must be ints")

        file_ids_str = ", ".join(str(file_id) for file_id in file_ids)

        sql = f"""
        SELECT
            MetadataApplication.file_id,
            MetadataApplication.metadata_id,
            File.hyperthought_id,
            Metadata.metadata
        FROM
            File
            INNER JOIN MetadataApplication
                ON File.id = MetadataApplication.file_id
            INNER JOIN Metadata
                ON Metadata.id = MetadataApplication.metadata_id
        WHERE
            File.id IN ({file_ids_str})
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)

        for row in cursor.fetchall():
            yield {
                key: row[key]
                for key in row.keys()
            }

        cursor.close()

    def delete_metadata(self, metadata_id: int, commit: bool = True) -> None:
        """Remove a Metadata record."""
        sql = "DELETE FROM Metadata WHERE id = :metadata_id"
        cursor = self.connection.cursor()
        cursor.execute(sql, {"metadata_id": metadata_id})

        if commit:
            self.connection.commit()

        cursor.close()

    def delete_metadata_application(
        self,
        metadata_id: int,
        commit: bool = True,
    ) -> None:
        """Remove MetadataApplication records associated with a metadata id."""
        sql = """
        DELETE
        FROM MetadataApplication
        WHERE metadata_id = :metadata_id
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"metadata_id": metadata_id})

        if commit:
            self.connection.commit()

        cursor.close()

    def delete_parser(self, parser_id: int, commit: bool = True) -> None:
        """Delete a parser."""
        sql = """
        DELETE
        FROM Parser
        WHERE id = :parser_id
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"parser_id": parser_id})

        if commit:
            self.connection.commit()

        cursor.close()
