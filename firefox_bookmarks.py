import sqlite3, time
from flask import Flask, jsonify, request, render_template
from benedict import benedict

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

DATABASE="places.sqlite"

@app.route('/')
def get_bookmarks():
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
			SELECT moz_places.id, moz_bookmarks.title, moz_places.url, moz_bookmarks.dateAdded
			FROM moz_places
			JOIN moz_bookmarks
			ON moz_places.id = moz_bookmarks.fk
			WHERE moz_bookmarks.parent = ?
		""", parent): # Get list of bookmarks & URLs for this folder
			bookmarks[tree][data['id']]={
				"title": data['title'],
				"url": data['url'],
				"date": time.strftime('%a, %d-%m-%Y %T', time.localtime(data['dateAdded']/1000000))
				} # Add the bookmarks to their parent folder
			# See also: datetime.fromtimestamp(data['dateAdded']/1000000)
			# https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR/Reference/PRTime - Mozilla uses microseconds, hence divide by 10^6
	
	return bookmarks

@app.route('/add', methods=['POST', 'GET'])
def add_bookmark():
	status = None
	if request.method == 'POST':
		try:
			conn = sqlite3.connect(DATABASE)
			c = conn.cursor()
			
			folder=(request.form['folder'],)
			# Currently, this returns the first occurrence of 'folder' - if there are multiple folders with the same name, this may cause unexpected results
			# TODO: Replace text field with drop-down on template, with parent name as hint => return ID
			parent=c.execute("""
				SELECT id
				FROM moz_bookmarks
				WHERE title = ?
				""", folder).fetchone() # Get id of named folder
			if not parent: raise KeyError # Folder does not exist - TODO: handle folder creation here
			
			position=c.execute("""
				SELECT MAX(position)
				FROM moz_bookmarks
				WHERE parent = ?
				""", parent).fetchone()[0]+1 # Get the next position for bookmark within folder
			
			parent=parent[0]
			
			fk=c.execute("SELECT MAX(id) FROM moz_places").fetchone()[0]+1 # Get the next id/foreign key for url reference
			
			url=request.form['url']
			
			title=request.form['title']
			
			date=time.time()*1000000

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
			status = "{0} ({1}) added to {2}.".format(title, url, folder[0])
		except KeyError:
			status = "Invalid folder name."
	return render_template('add_bookmark.html', status=status)

if __name__ == "__main__": app.run()
