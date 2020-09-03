import sqlite3
from flask import Flask, jsonify
from benedict import benedict
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def json_bookmarks():
	conn = sqlite3.connect("places.sqlite")
	#conn.row_factory = sqlite3.Row
	c = conn.cursor()
	bookmarks=benedict()
	
	folders_data = c.execute("""
		SELECT b1.id, b1.parent, b1.title, b2.title
		FROM moz_bookmarks as b1
		LEFT OUTER JOIN moz_bookmarks as b2
		WHERE b1.fk IS NULL
		AND b1.parent = b2.id
		ORDER BY b1.parent ASC, b1.position ASC
	""").fetchall()
	
	for folder in folders_data:
		if folder[1] == 0 or folder[2] == None: continue # Already at top
		folder_parent=(folder[1],)
		tree=[]
		while True: # Get keylist for benedict
			p_info=c.execute("SELECT parent, title FROM moz_bookmarks WHERE id = ?", folder_parent).fetchone()
			if p_info[0] == 0: break # Reached the top
			else:
				tree.insert(0, p_info[1])
				folder_parent=(p_info[0],) # Process next parent
		tree.append(folder[2])
		
		bookmarks[tree]={} # Create empty dictionary for bookmarks
		parent=(folder[0],)
		for data in c.execute("""
			SELECT moz_places.id, moz_bookmarks.title, moz_places.url, moz_bookmarks.dateAdded
			FROM moz_places
			JOIN moz_bookmarks
			ON moz_places.id = moz_bookmarks.fk
			WHERE moz_bookmarks.parent = ?
		""", parent):
			bookmarks[tree][data[0]]={"title": data[1], "url": data[2], "date": datetime.fromtimestamp(data[3]/1000000)} # Add the bookmarks to their parent folder
			# See also: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[3]/1000000))
			# https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR/Reference/PRTime - Mozilla uses microseconds, hence divide by 10^6
	
	return jsonify(bookmarks)

if __name__ == "__main__": app.run()
