"""
database/upload/connect.py

Means of connecting to upload database.
"""

import os
import shutil
import sqlite3


def get_connection(binner_path, overwrite=True):
    """
    Get or create a database file for a manifest.

    Parameters
    ----------
    binner_path : str
        Path to the binner database file to be opened or created.
    overwrite : bool
        If True, and a file already exists, replace file with new file.

    Returns
    -------
    A connection to the SQLite database.
    """
    template_path = os.path.join(
        os.path.dirname(__file__),
        "template",
        "template.db",
    )

    if not os.path.exists(binner_path) or overwrite:
        shutil.copyfile(template_path, binner_path)

    # Open a connection to the database file.
    # Detect types like DATETIME, which will then be treated as datetime
    # objects instead of strings.
    conn = sqlite3.connect(binner_path, detect_types=sqlite3.PARSE_DECLTYPES)

    # Allow values in records to be retrieved using column names as keys.
    conn.row_factory = sqlite3.Row

    # Enforce referential integrity.
    conn.execute("PRAGMA foreign_keys = ON")

    return conn
