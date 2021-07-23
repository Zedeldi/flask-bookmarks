"""Import app blueprints."""

from flask_bookmarks.core.add_bookmark import add_page
from flask_bookmarks.core.errors import error_pages
from flask_bookmarks.core.get_bookmarks import get_page

blueprints = [
    add_page,
    error_pages,
    get_page,
]
