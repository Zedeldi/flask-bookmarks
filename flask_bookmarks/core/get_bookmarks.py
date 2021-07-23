"""Return bookmarks in JSON or HTML."""

import sqlite3
import time
from typing import Union

from benedict import benedict
from flask import Blueprint, current_app, flash, render_template, request

from flask_bookmarks.utils import export_html

get_page = Blueprint("get_page", __name__)


@get_page.route("/")
def get_bookmarks() -> Union[str, benedict]:
    """Return bookmarks in JSON or HTML format."""
    use_html = request.args.get("html", default=False)
    if isinstance(use_html, str):
        use_html = use_html.lower() in ("true", "yes", "y", "on", "1")

    try:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        # Get dictionary-like objects for readability
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        bookmarks = benedict()

        folders_data = c.execute(
            """
            SELECT id, parent, title
            FROM moz_bookmarks
            WHERE fk IS NULL
            ORDER BY parent ASC, position ASC
            """
        ).fetchall()  # Get list of all folders

        for folder in folders_data:
            if folder["parent"] == 0 or folder["title"] is None:
                # Already at top, ignore
                continue
            folder_parent = (folder["parent"],)
            tree = [folder["title"]]
            while True:  # Get keylist for benedict
                p_info = c.execute(
                    "SELECT parent, title FROM moz_bookmarks WHERE id = ?",
                    folder_parent,
                ).fetchone()
                if p_info["parent"] == 0:
                    # Reached the top
                    break
                else:
                    tree.insert(0, p_info["title"])  # Prepend parent title to tree
                    folder_parent = (p_info["parent"],)  # Process next parent

            bookmarks[tree] = {}  # Create empty dictionary for bookmarks
            parent = (folder["id"],)
            for data in c.execute(
                """
                SELECT \
                    moz_places.id,
                    moz_bookmarks.title,
                    moz_places.url,
                    moz_bookmarks.dateAdded,
                    moz_bookmarks.lastModified
                FROM moz_places
                JOIN moz_bookmarks
                ON moz_places.id = moz_bookmarks.fk
                WHERE moz_bookmarks.parent = ?
                """,
                parent,
            ):  # Get list of bookmarks & URLs for this folder
                bookmarks[tree][data["id"]] = {
                    "title": data["title"],
                    "url": data["url"],
                    "date": data["dateAdded"] / 1000000,
                    "modified": data["lastModified"] / 1000000,
                }  # Add the bookmarks to their parent folder
                # See also: time.strftime() and datetime.fromtimestamp()
                # to convert Unix time
                # https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR/Reference/PRTime
                # Mozilla uses microseconds resolution, hence divide by 10^6
    except sqlite3.OperationalError as e:  # DB is probably invalid
        flash("Database operation error ({0}).".format(e))
        return render_template("error.html")  # Handle with error template

    if use_html:
        filename = "bookmarks{0}.html".format(
            time.strftime("-%Y-%m-%d", time.localtime())
        )
        # Create file descriptor outside of recursive function, overwrites if exists
        with open(filename, "w+") as fd:
            export_html(bookmarks, fd)  # Recursively parse JSON and write HTML to file
            fd.seek(0)
            if current_app.config["USE_FIREFOX_HTML"]:
                return fd.read()  # Return the HTML
            else:
                return render_template("get_bookmarks.html", bookmarks=fd.read())

    return bookmarks  # Else, return the JSON/dict
