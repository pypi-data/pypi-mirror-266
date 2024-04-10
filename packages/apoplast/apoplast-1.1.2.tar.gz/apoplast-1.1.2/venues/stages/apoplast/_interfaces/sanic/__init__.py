
'''
	python3 /apoplast/venues/stages/apoplast/_interfaces/sanic/__init__.py
	
	sanic /apoplast/venues/stages/apoplast/_interfaces/sanic
'''

def add_paths_to_system (paths):
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_directory, path)))

add_paths_to_system ([
	'../../../../stages',
	'../../../../stages_pip'
])

'''
	https://sanic.dev/en/guide/running/manager.html#dynamic-applications
'''

from sanic import Sanic
from sanic.response import text

app = Sanic (__name__)

# Define a route
@app.route ("/")
async def hello(request):
	return text ("Hello, Sanic!")

'''
from apoplast._variables import prepare_variables


def main ():
	apoplast_variables = prepare_variables ({
		"moon": {}
	})

	# Create a Sanic app
	app = Sanic(__name__)

	# Define a route
	@app.route("/")
	async def hello(request):
		return text("Hello, Sanic!")

	return [ app, apoplast_variables ["harbor"] ["PID_path"] ]
'''

'''
if __name__ == "__main__":
	[ app, pid_file ] = main ()
	app.run (host = "0.0.0.0", port = 8000)
'''