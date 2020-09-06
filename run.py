#!/usr/bin/env python3

from flask_bookmarks import app
from flask_bookmarks.utils import check_database

if __name__ == "__main__":
	check_database()
	app.run()
