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
flask_bookmarks.core.errors

Defines handlers for HTTP error codes.
"""

from flask import flash, render_template

from flask_bookmarks import app


@app.errorhandler(403)
def forbidden(e):
	flash("You are not allowed to do that!")
	return render_template("error.html"), 403


@app.errorhandler(404)
def page_not_found(e):
	flash("That page does not exist!")
	return render_template("error.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
	flash("An unexpected error has occurred.")
	return render_template("error.html"), 500
