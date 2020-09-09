# flask-bookmarks

[![GitHub license](https://img.shields.io/github/license/Zedeldi/flask-bookmarks?style=flat-square)](https://github.com/Zedeldi/flask-bookmarks/blob/master/LICENSE) [![GitHub last commit](https://img.shields.io/github/last-commit/Zedeldi/flask-bookmarks?style=flat-square)](https://github.com/Zedeldi/flask-bookmarks/commits)

Flask front-end for handling Firefox's bookmarks with Python.

## Description

flask-bookmarks uses Firefox's [`places.sqlite`](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/Places/Database) database to store/retrieve bookmarks, in hope to create a self-hosted, centralised location for them, accessible from any device, whilst maintaining integrity of the database to be used by the browser.

## Installation

1. Clone this repo: `git clone https://github.com/Zedeldi/flask-bookmarks.git`
2. Install required Python modules: `pip3 install -r requirements.txt`
3. Modify `config.py`
   - `DATABASE` should refer to a valid Firefox `places.sqlite`
   - Change `SECRET_KEY` in production environments
4. Run: `python3 run.py` or `python3 run.py waitress`

To run with a standalone WSGI server or behind a HTTP proxy, read this [documentation](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/).

e.g.

 - `gunicorn -b 127.0.0.1:8080 flask_bookmarks:app`
 - `waitress-serve --listen=127.0.0.1:8080 flask_bookmarks:app`

Libraries:

- [Flask](https://pypi.org/project/Flask/) - WSGI web application framework
- [Waitress](https://pypi.org/project/waitress/) - production WSGI server
- [python-benedict](https://pypi.org/project/python-benedict/) - dict keylist support

## Usage

At `/`, bookmarks will be returned in JSON, by default. Pass `?html=True` as a query in the URL to format as HTML. Set `USE_FIREFOX_HTML` in `config.py` to output HTML in a similar format as Firefox's exports, else it will extend `layout.html`.

To add bookmarks through the web interface, go to `/add`.

## Todo

- Makefile, setup automation

## License

flask-bookmarks is licensed under the GPL v3 for everyone to use, modify and share freely.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

[![GPL v3 Logo](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl-3.0-standalone.html)

## Credits

Bootstrap = <https://getbootstrap.com/>

## Donate

If you found this project useful, please consider donating. Any amount is greatly appreciated! Thank you :smiley:

My bitcoin address is: [bc1q5aygkqypxuw7cjg062tnh56sd0mxt0zd5md536](bitcoin://bc1q5aygkqypxuw7cjg062tnh56sd0mxt0zd5md536)
