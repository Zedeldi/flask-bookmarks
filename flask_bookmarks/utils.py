"""Various helper functions for database operations and processing."""

import sqlite3
import time
from typing import TextIO

from benedict import benedict
from flask import current_app


# DATABASE FUNCTIONS #
def check_database() -> None:
    """
    Check that the database has necessary tables.

    Raise DatabaseError if access failed, or database is malformed.
    """
    try:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        c = conn.cursor()
        if (
            len(
                c.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                    AND name='moz_bookmarks'
                    OR name='moz_places'
                    """
                ).fetchall()
            )
            != 2
        ):  # Check that moz_bookmarks and moz_places exist
            raise sqlite3.DatabaseError("Invalid database.")
    except sqlite3.OperationalError as e:
        # Permissions?
        raise sqlite3.DatabaseError("Database operation error ({0}).".format(e))
    else:
        # All is okay :)
        conn.close()


def get_next_position(parent: int) -> int:
    """Return the next available position in parent."""
    conn = sqlite3.connect(current_app.config["DATABASE"])
    c = conn.cursor()
    t = (parent,)
    # Get the next position for bookmark within folder
    position = c.execute(
        """
        SELECT MAX(position)
        FROM moz_bookmarks
        WHERE parent = ?
        """,
        t,
    ).fetchone()[0]
    # Return 0 if nothing is in folder (it has no children yet)
    return position + 1 if position is not None else 0


def create_folder(title: str, parent: int = 3) -> int:
    """
    Create a folder (fk == NULL) at the next available position in parent.

    Parameters:
        title: name for the folder
        parent: where the folder is located (default: 3)

    Returns:
        id of the new folder
    """
    conn = sqlite3.connect(current_app.config["DATABASE"])
    c = conn.cursor()
    position = get_next_position(parent)

    date = time.time() * 1000000  # Omit the decimal point

    folder = (parent, position, title, date, date)
    c.execute(
        """
        INSERT INTO moz_bookmarks (
            type, fk, parent, position, title, dateAdded, lastModified
        )
        VALUES (2, NULL, ?, ?, ?, ?, ?)
        """,
        folder,
    )  # Add the folder
    conn.commit()  # Save changes

    # Race-conditions may occur with this method on multi-threaded servers
    return c.execute("SELECT max(id) FROM moz_bookmarks").fetchone()[0]


# EXPORT FUNCTIONS #
def export_html(d: benedict, fd: TextIO, n: int = 1) -> None:
    """
    Write HTML to fd with values from d, following the syntax of Firefox.

    Recursively walks through dictionary to distinguish between folders
    and bookmarks.

    Parameters:
        d: dictionary to process
        fd: open file descriptor
        n: current depth of recursion for heading size (max = 6)
    """
    if current_app.config["USE_FIREFOX_HTML"]:
        # Match Firefox's uniform heading size
        n = 3
    elif n > 6:
        n = 6
    for key in d:
        try:
            fd.write(
                """
    <DT><A HREF="{0}"
    ADD_DATE="{1}"
    LAST_MODIFIED="{2}">
    {3}
    </A>""".format(
                    d[key]["url"], d[key]["date"], d[key]["modified"], d[key]["title"]
                )
            )
        except KeyError:
            # d[key] is a folder
            fd.write(
                """
</DL><p>
<DT><H{0}>{1}</H{0}>
<DL><p>""".format(
                    n, key
                )
            )
            export_html(d[key], fd, n + 1)  # Recursively parse children
