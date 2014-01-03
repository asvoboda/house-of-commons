from hansard import app
import os

debug = True
if 'DATABASE_URL' in os.environ:
    debug = False

app.run(debug=debug)