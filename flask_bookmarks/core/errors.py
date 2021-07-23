"""Define handlers for HTTP error codes."""

from typing import Tuple

from flask import Blueprint, flash, render_template

error_pages = Blueprint("error_pages", __name__)


@error_pages.app_errorhandler(403)
def forbidden(e) -> Tuple[str, int]:
    """Error 403 (forbidden) handler."""
    flash("You are not allowed to do that!")
    return render_template("error.html"), 403


@error_pages.app_errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    """Error 404 (not found) handler."""
    flash("That page does not exist!")
    return render_template("error.html"), 404


@error_pages.app_errorhandler(500)
def internal_server_error(e) -> Tuple[str, int]:
    """Error 500 (internal error) handler."""
    flash("An unexpected error has occurred.")
    return render_template("error.html"), 500
