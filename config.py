"""Configuration for flask-bookmarks and Flask application."""

DATABASE = "places.sqlite"
USE_FIREFOX_HTML = False

# Built-in Flask config
JSON_SORT_KEYS = False
SECRET_KEY = "development"  # Change this, e.g. os.urandom(16)
