from hansard import app
import os

debug = True
if os.environ.has_key('DATABASE_URL'):
	debug = False

app.run(debug=debug)