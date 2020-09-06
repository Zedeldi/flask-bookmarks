import sqlite3, time
from config import *

## DATABASE FUNCTIONS ##
def check_database():
	"""Check that the database has necessary tables."""
	try:
		conn = sqlite3.connect(DATABASE)
		c = conn.cursor()
		if len(c.execute("""
			SELECT name
			FROM sqlite_master
			WHERE type='table'
			AND name='moz_bookmarks'
			OR name='moz_places'
		""").fetchall()) != 2: # Check that moz_bookmarks and moz_places exist
			print("Invalid database.")
			exit(1)
	except sqlite3.OperationalError as e: # Permissions?
		print("Database operation error ({0}).".format(e))
		exit(1)
	else: conn.close() # All is okay :)

def get_next_position(parent):
	"""Return the next available position in parent."""
	conn = sqlite3.connect(DATABASE)
	c = conn.cursor()
	t=(parent,)
	position=c.execute("""
		SELECT MAX(position)
		FROM moz_bookmarks
		WHERE parent = ?
		""", t).fetchone()[0] # Get the next position for bookmark within folder
	return position+1 if position != None else 0 # In case nothing is in folder (it has no children yet)

def create_folder(title, parent=3): # Default parent is toolbar for Firefox's sake
	"""
	Creates a folder (fk == NULL) at the next available position in parent.
	
	Parameters:
	title (string): name for the folder
	parent (int): where the folder is located (default: 3)
	
	Returns:
	int: id of the new folder
	"""
	conn = sqlite3.connect(DATABASE)
	c = conn.cursor()
	position=get_next_position(parent)
	
	date=time.time()*1000000 # Omit the decimal point

	folder=(parent, position, title, date, date)
	c.execute("""
		INSERT INTO moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified)
		VALUES (2, NULL, ?, ?, ?, ?, ?)
	""", folder) # Add the folder
	conn.commit() # Save changes
	
	# Race-conditions may occur with this method on multi-threaded servers
	return c.execute('SELECT max(id) FROM moz_bookmarks').fetchone()[0]

## EXPORT FUNCTIONS ##
def export_html(d, fd):
	"""
	Writes HTML to fd with values from d, following the syntax of Firefox's export.
	
	Recursively walks through dictionary to distinguish between folders and bookmarks.
	
	Parameters:
	d (dict): dictionary to process
	fd (file): open file descriptor
	"""
	for key in d:
		try: fd.write("""
	<DT><A HREF="{0}" 
	ADD_DATE="{1}" 
	LAST_MODIFIED="{2}">
	{3}
	</A>
		""".format(d[key]['url'], d[key]['date'], d[key]['modified'], d[key]['title']))
		except KeyError: # d[key] is a folder
			fd.write("""
</DL><p>
<DT><H3>{0}</H3>
<DL><p>
			""".format(key))
			export_html(d[key], fd) # Recursively parse children
