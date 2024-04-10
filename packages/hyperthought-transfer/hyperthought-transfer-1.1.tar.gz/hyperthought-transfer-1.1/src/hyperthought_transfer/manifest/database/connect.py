"""
database/upload/connect.py

Means of connecting to upload database.
"""

import json
import os
import shutil
import sqlite3
from sqlite3 import Connection


# Register adapter and converter for "BOOLEAN" type.
sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda db_value: bool(int(db_value)))

# Register adapter and converter for "METADATA" type.
sqlite3.register_adapter(dict, json.dumps)  # TODO:  Is this needed?
sqlite3.register_adapter(list, json.dumps)
sqlite3.register_adapter(tuple, json.dumps)  # TODO:  Is this needed?
sqlite3.register_converter("METADATA", lambda db_value: json.loads(db_value))


# Time to wait until timeout due to database locking.
BUSY_TIMEOUT = 30_000  # ms


def is_parent(parent_path: str, source_path: str) -> bool:
    """
    Determine whether a path is the parent of the source path.

    Will be used in SQL.
    """
    if not parent_path or not source_path:
        return False

    return parent_path == os.path.dirname(source_path)


def is_parent_progeny(progeny_path: str, source_path: str) -> bool:
    """
    Determine whether a path is the progeny of the parent of the source path.

    Will be used in SQL.
    """
    if not progeny_path or not source_path:
        return False

    parent_path = os.path.dirname(source_path)
    return parent_path != progeny_path and progeny_path.startswith(parent_path)


def is_sibling(sibling_path: str, source_path: str) -> bool:
    """
    Determine whether a path is the sibling of the source path.

    Will be used in SQL.
    """
    if not sibling_path or not source_path:
        return False

    return (
        os.path.dirname(source_path) == os.path.dirname(sibling_path)
        and
        source_path != sibling_path
    )


def get_connection(manifest_path: str, overwrite: bool = True) -> Connection:
    """
    Get or create a database file for a manifest.

    Parameters
    ----------
    manifest_path : str
        Path to the manifest database file to be opened or created.
    overwrite : bool
        If True, and a file already exists, replace file with new file.

    Returns
    -------
    A connection to the SQLite database.
    """
    template_path = os.path.join(
        os.path.dirname(__file__),
        "template/template.db",
    )

    if not os.path.exists(manifest_path) or overwrite:
        shutil.copyfile(template_path, manifest_path)

    # Open a connection to the database file.
    # Detect types like DATETIME, which will then be treated as datetime
    # objects instead of strings.
    conn = sqlite3.connect(manifest_path, detect_types=sqlite3.PARSE_DECLTYPES)

    # Allow values in records to be retrieved using column names as keys.
    conn.row_factory = sqlite3.Row

    # Enforce referential integrity.
    conn.execute("PRAGMA foreign_keys = ON")

    # Specify time to wait for a database lock.
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT}")

    # Create SQL functions.
    conn.create_function("IsParent", 2, is_parent)
    conn.create_function("IsParentProgeny", 2, is_parent_progeny)
    conn.create_function("IsSibling", 2, is_sibling)

    return conn
