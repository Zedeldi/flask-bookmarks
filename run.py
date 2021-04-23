#!/usr/bin/env python3

import sys

from flask_bookmarks import app
from flask_bookmarks.utils import check_database

HOST = "127.0.0.1"
PORT = 8080
THREADS = 4  # For waitress

if __name__ == "__main__":
	check_database()
	try:
		if sys.argv[1] == "waitress":
			from waitress import serve
			serve(app, host=HOST, port=PORT, threads=THREADS)
	except IndexError:
		app.run(host=HOST, port=PORT)
