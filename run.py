#!/usr/bin/env python3

"""
Check database and start server.

Use waitress if specified.
"""

import sys
from sqlite3 import DatabaseError

from flask_bookmarks import app
from flask_bookmarks.utils import check_database

HOST = "127.0.0.1"
PORT = 8080
THREADS = 4  # For waitress

if __name__ == "__main__":
    try:
        check_database()
    except DatabaseError as e:
        print(e)
        sys.exit(1)
    try:
        if sys.argv[1] == "waitress":
            from waitress import serve

            serve(app, host=HOST, port=PORT, threads=THREADS)
    except IndexError:
        app.run(host=HOST, port=PORT)
