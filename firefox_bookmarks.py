import sqlite3, time

from flask import Flask, request, render_template
from benedict import benedict

from config import *
from utils import *

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def get_bookmarks():
	use_html = request.args.get('html', default=False)
	
	conn = sqlite3.connect(DATABASE)
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
		
	if use_html:
		filename="bookmarks{0}.html".format(time.strftime('-%Y-%m-%d', time.localtime()))
		with open(filename, 'w+') as fd: # Create file descriptor outside of recursive function, overwrites if exists
			export_html(bookmarks, fd) # Recursively parse JSON and write HTML to file
			fd.seek(0)
			return fd.read() # Return the HTML
	
	return bookmarks # Else, return the JSON/dict

@app.route('/add', methods=['POST', 'GET'])
def add_bookmark():
	status = None
	if request.method == 'POST':
		try:
			conn = sqlite3.connect(DATABASE)
			c = conn.cursor()
			
			path=request.form['folder'].strip('/').split('/') # Remove leading/trailing slashes
			title=(path[0],)
			# Currently, this returns the first occurrence of 'title' - if there are multiple folders with the same name, you should specify an explicit path
			# TODO: Replace text field with drop-down on template, with parent name as hint => return ID
			try:
				parent=c.execute("""
					SELECT id
					FROM moz_bookmarks
					WHERE fk IS NULL
					AND title = ?
					""", title).fetchone()[0] # Get id of initial parent
			except TypeError: parent=create_folder(path[0]) # Initial folder does not exist - create it
			last_parent=parent
			for title in path[1:]:
				t=(title, parent) # Traverse down folder tree
				try:
					parent=c.execute("""
						SELECT id
						FROM moz_bookmarks
						WHERE fk IS NULL
						AND title = ?
						AND parent = ?
						""", t).fetchone()[0] # Find matching child of parent
				except TypeError: parent=create_folder(title, last_parent) # Use the last existing folder as its parent
				last_parent=parent
			
			position=get_next_position(parent)
			
			fk=c.execute("SELECT MAX(id) FROM moz_places").fetchone()[0]+1 # Get the next id/foreign key for url reference
			
			url=request.form['url']
			
			title=request.form['title']
			
			date=time.time()*1000000 # Omit the decimal point

			place=(fk, url, title)
			c.execute("""
				INSERT INTO moz_places (id, url, title)
				VALUES (?, ?, ?)
			""", place) # Add the url reference to moz_places

			bookmark=(fk, parent, position, title, date, date)
			c.execute("""
				INSERT INTO moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified)
				VALUES (1, ?, ?, ?, ?, ?, ?)
			""", bookmark) # Add the bookmark
			conn.commit() # Save changes
			status = "{0} ({1}) added to {2}.".format(title, url, request.form['folder'])
		except (KeyError, TypeError) as e:
			status = "Invalid input ({0}).".format(e) # Blame the user
		except sqlite3.OperationalError as e: # DB is probably locked
			status = "Database operation error ({0}).".format(e)
	return render_template('add_bookmark.html', status=status)

if __name__ == "__main__":
	check_database()
	app.run()
