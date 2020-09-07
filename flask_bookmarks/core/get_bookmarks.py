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
flask_bookmarks.core.get_bookmarks

Returns bookmarks in JSON or HTML.
"""

import sqlite3, time

from flask import flash, render_template, request
from benedict import benedict

from flask_bookmarks import app
from flask_bookmarks.utils import export_html

@app.route('/')
def get_bookmarks():
	use_html = request.args.get('html', default=False)
	
	try:
		conn = sqlite3.connect(app.config['DATABASE'])
		conn.row_factory = sqlite3.Row # Get dictionary-like objects for readability
		c = conn.cursor()
		bookmarks=benedict()
		
		folders_data = c.execute("""
			SELECT id, parent, title
			FROM moz_bookmarks
			WHERE fk IS NULL
			ORDER BY parent ASC, position ASC
		""").fetchall() # Get list of all folders
		
		for folder in folders_data:
			if folder['parent'] == 0 or folder['title'] == None: continue # Already at top, ignore
			folder_parent=(folder['parent'],)
			tree=[folder['title']]
			while True: # Get keylist for benedict
				p_info=c.execute("SELECT parent, title FROM moz_bookmarks WHERE id = ?", folder_parent).fetchone()
				if p_info['parent'] == 0: break # Reached the top
				else:
					tree.insert(0, p_info['title']) # Prepend parent title to tree
					folder_parent=(p_info['parent'],) # Process next parent
			
			bookmarks[tree]={} # Create empty dictionary for bookmarks
			parent=(folder['id'],)
			for data in c.execute("""
				SELECT moz_places.id, moz_bookmarks.title, moz_places.url, moz_bookmarks.dateAdded, moz_bookmarks.lastModified
				FROM moz_places
				JOIN moz_bookmarks
				ON moz_places.id = moz_bookmarks.fk
				WHERE moz_bookmarks.parent = ?
			""", parent): # Get list of bookmarks & URLs for this folder
				bookmarks[tree][data['id']]={
					"title": data['title'],
					"url": data['url'],
					"date": data['dateAdded']/1000000,
					"modified": data['lastModified']/1000000
					} # Add the bookmarks to their parent folder
				# See also: time.strftime('%a, %d-%m-%Y %T', time.localtime(data['dateAdded']/1000000)),
				# and: datetime.fromtimestamp(data['dateAdded']/1000000) to convert Unix time
				# https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR/Reference/PRTime - Mozilla uses microseconds resolution, hence divide by 10^6
	except sqlite3.OperationalError as e: # DB is probably invalid
		flash("Database operation error ({0}).".format(e))
		return render_template("error.html") # Handle with error template
		
	if use_html:
		filename="bookmarks{0}.html".format(time.strftime('-%Y-%m-%d', time.localtime()))
		with open(filename, 'w+') as fd: # Create file descriptor outside of recursive function, overwrites if exists
			export_html(bookmarks, fd) # Recursively parse JSON and write HTML to file
			fd.seek(0)
			return fd.read() # Return the HTML
	
	return bookmarks # Else, return the JSON/dict
