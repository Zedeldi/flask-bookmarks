"""Process request to add bookmark, creating folders where necessary."""

import sqlite3
import time

from flask import Blueprint, current_app, render_template, request

from flask_bookmarks.utils import create_folder, get_next_position

add_page = Blueprint("add_page", __name__)


@add_page.route("/add", methods=["POST", "GET"])
def add_bookmark() -> str:
    """Handle adding bookmarks and creating parents."""
    status = None
    if request.method == "POST":
        try:
            conn = sqlite3.connect(current_app.config["DATABASE"])
            c = conn.cursor()

            # Remove leading/trailing slashes
            path = request.form["folder"].strip("/").split("/")
            title = path[0]
            # Currently, this returns the first occurrence of 'title'
            # If there are multiple folders with the same name, you should
            # specify an explicit path
            # TODO: Replace text field with drop-down on template, with parent
            # name as hint => return ID
            try:
                # Get id of initial parent
                parent = c.execute(
                    """
                    SELECT id
                    FROM moz_bookmarks
                    WHERE fk IS NULL
                    AND title = ?
                    """,
                    (title,),
                ).fetchone()[0]
            except TypeError:
                # Initial folder does not exist - create it
                parent = create_folder(path[0])
            last_parent = parent
            for title in path[1:]:
                t = (title, parent)  # Traverse down folder tree
                try:
                    # Find matching child of parent
                    parent = c.execute(
                        """
                        SELECT id
                        FROM moz_bookmarks
                        WHERE fk IS NULL
                        AND title = ?
                        AND parent = ?
                        """,
                        t,
                    ).fetchone()[0]
                except TypeError:
                    # Use the last existing folder as its parent
                    parent = create_folder(title, last_parent)
                last_parent = parent

            position = get_next_position(parent)

            # Get the next id/foreign key for url reference
            fk = c.execute("SELECT MAX(id) FROM moz_places").fetchone()[0] + 1

            url = request.form["url"]

            title = request.form["title"]

            date = time.time() * 1000000  # Omit the decimal point

            place = (fk, url, title)
            c.execute(
                """
                INSERT INTO moz_places (id, url, title)
                VALUES (?, ?, ?)
                """,
                place,
            )  # Add the url reference to moz_places

            bookmark = (fk, parent, position, title, date, date)
            c.execute(
                """
                INSERT INTO moz_bookmarks (
                    type, fk, parent, position, title, dateAdded, lastModified
                )
                VALUES (1, ?, ?, ?, ?, ?, ?)
                """,
                bookmark,
            )  # Add the bookmark
            conn.commit()  # Save changes
            status = "{0} ({1}) added to {2}.".format(
                title, url, request.form["folder"]
            )
        except (KeyError, TypeError) as e:
            status = "Invalid input ({0}).".format(e)  # Blame the user
        except sqlite3.OperationalError as e:  # DB is probably locked
            status = "Database operation error ({0}).".format(e)
    return render_template("add_bookmark.html", status=status)
