# flask-bookmarks
# Copyright (C) 2020  Zack Didcott

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
flask_bookmarks.utils

Various helper functions for database operations and processing.
"""

import sqlite3
import time
from flask_bookmarks import app


# DATABASE FUNCTIONS #
def check_database():
    """Check that the database has necessary tables."""
    try:
        conn = sqlite3.connect(app.config["DATABASE"])
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
            print("Invalid database.")
            exit(1)
    except sqlite3.OperationalError as e:
        # Permissions?
        print("Database operation error ({0}).".format(e))
        exit(1)
    else:
        # All is okay :)
        conn.close()


def get_next_position(parent):
    """Return the next available position in parent."""
    conn = sqlite3.connect(app.config["DATABASE"])
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


def create_folder(title, parent=3):
    """
    Creates a folder (fk == NULL) at the next available position in parent.

    Parameters:
    title (string): name for the folder
    parent (int): where the folder is located (default: 3)

    Returns:
    int: id of the new folder
    """
    conn = sqlite3.connect(app.config["DATABASE"])
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
def export_html(d, fd, n=1):
    """
    Writes HTML to fd with values from d, following the syntax of
    Firefox's export.

    Recursively walks through dictionary to distinguish between folders
    and bookmarks.

    Parameters:
    d (dict): dictionary to process
    fd (file): open file descriptor
    n (int): current depth of recursion for heading size (max = 6)
    """
    if app.config["USE_FIREFOX_HTML"]:
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
