

'''
	mongo connection strings
		
		DB: apoplast
			
			collection: 
				cautionary_ingredients
				essential_nutrients
'''



def add_paths_to_system (paths):
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_directory, path)))

add_paths_to_system ([
	'../../../stages_pip'
])


import json
import pathlib
from os.path import dirname, join, normpath

name = "apoplast"


this_directory = pathlib.Path (__file__).parent.resolve ()
venues = str (normpath (join (this_directory, "../../../../venues")))
this_stage = str (normpath (join (venues, f"stages/{ name }")))

#glob_string = venues + '/stages/**/status_*.py'

import sys
if (len (sys.argv) >= 2):
	glob_string = this_stage + '/' + sys.argv [1]
	db_directory = False
else:
	glob_string = this_stage + '/**/status_*.py'
	db_directory = normpath (join (this_directory, "db"))

print ("glob string:", glob_string)

import volts
scan = volts.start (
	glob_string = glob_string,
	simultaneous = True,
	module_paths = [
		normpath (join (venues, "stages")),
		normpath (join (venues, "stages_pip"))
	],
	relative_path = this_stage,
	
	db_directory = db_directory
)
