"""
Database functionality for a file binner.

An object of class Database is available via the `database` property of a
binner object.
"""
from collections import defaultdict
import sqlite3
from typing import Dict
from typing import List
from typing import Optional


from . import connect, template  # noqa: F401


class Database:
    """
    Manager class for a file binner embedded database.

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
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def create_bin(self) -> int:
        """
        Create a bin and return the bin id.
        """
        sql = "INSERT INTO Bin DEFAULT VALUES"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        bin_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return bin_id

    def create_file(
        self,
        process_id: str,
        manifest_file_id: int,
        file_size: int,
        bin_id: int,
    ) -> int:
        """
        Create a file record in the database.

        Parameters
        ----------
        process_id : str
            The id of the process running the job/manifest associated with the
            file.
        manifest_file_id : int
            The id of the file in the manifest database.
        file_size : int
            The size of the file.
        bin_id : int
            The id of the bin associated with the file.
        commit : bool
            If True, commit changes to the database.

        Returns
        -------
        The id for the file.
        """
        sql = """
        INSERT INTO File (
            process_id,
            manifest_file_id,
            file_size,
            bin_id
        ) VALUES (
            :process_id,
            :manifest_file_id,
            :file_size,
            :bin_id
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {
            "process_id": process_id,
            "manifest_file_id": manifest_file_id,
            "file_size": file_size,
            "bin_id": bin_id,
        })
        file_id = cursor.lastrowid

        # Do not commit changes, for performance reasons.
        cursor.close()
        return file_id

    def get_next_bin_id(self) -> Optional[int]:
        """Get the next available bin id."""
        sql = "SELECT MIN(id) AS bin_id FROM Bin"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()

        if not row:
            cursor.close()
            return None

        bin_id = row["bin_id"]
        cursor.close()
        return bin_id

    def get_bin_data(self, bin_id: int) -> Dict[str, List[int]]:
        """
        Get data on the active bin.

        Returns
        -------
        A dict with process ids for keys and lists of file ids for values.
        """
        sql = """
        SELECT process_id, manifest_file_id AS file_id
        FROM File
        WHERE bin_id = :bin_id
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, {"bin_id": bin_id})
        output = defaultdict(list)

        for row in cursor.fetchall():
            output[row["process_id"]].append(row["file_id"])

        cursor.close()
        return output

    def delete_bin(self, bin_id: int) -> None:
        """Delete a bin."""
        sql = "DELETE FROM Bin WHERE id = :bin_id"
        cursor = self.connection.cursor()
        cursor.execute(sql, {"bin_id": bin_id})
        cursor.close()
