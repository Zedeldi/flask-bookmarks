# flask-bookmarks

[![GitHub license](https://img.shields.io/github/license/Zedeldi/flask-bookmarks?style=flat-square)](https://github.com/Zedeldi/flask-bookmarks/blob/master/LICENSE) [![GitHub last commit](https://img.shields.io/github/last-commit/Zedeldi/flask-bookmarks?style=flat-square)](https://github.com/Zedeldi/flask-bookmarks/commits)

Flask front-end for handling Firefox's bookmarks with Python.

## Description

flask-bookmarks uses Firefox's [`places.sqlite`](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/Places/Database) database to store/retrieve bookmarks, in hope to create a self-hosted, centralised location for them, accessible from any device, whilst maintaining integrity of the database to be used by the browser.

## Installation

1. Clone this repo: `git clone https://github.com/Zedeldi/flask-bookmarks.git`
2. Install required Python modules: `pip3 install -r requirements.txt`
3. Run: `python3 run.py`

Libraries:

- [Flask](https://pypi.org/project/Flask/) - WSGI web application framework
- [python-benedict](https://pypi.org/project/python-benedict/) - dict keylist support

## Todo

- Error pages & handling

## License

flask-bookmarks is licensed under the GPL v3 for everyone to use, modify and share freely.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

[![GPL v3 Logo](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl-3.0-standalone.html)

## Credits

Bootstrap = <https://getbootstrap.com/>

## Donate

If you found this project useful, please consider donating. Any amount is greatly appreciated! Thank you :smiley:

My bitcoin address is: [bc1q5aygkqypxuw7cjg062tnh56sd0mxt0zd5md536](bitcoin://bc1q5aygkqypxuw7cjg062tnh56sd0mxt0zd5md536)
