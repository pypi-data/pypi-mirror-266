

'''
	mongod --dbpath ./../_mongo_data --port 39000
'''

'''
	import apoplast.data_nodes.ingredients.DB.open as ingredient_DB
	mongo_process = ingredient_DB.open (
		apoplast_variables = apoplast_variables
	)
	
	import time
	while True:
		time.sleep (1)
'''

'''	
	mongo_process.terminate ()

	#
	#	without this it might appear as if the process is still running.
	#
	import time
	time.sleep (2)
'''



import ships.cycle.loops as cycle_loops

import apoplast.data_nodes.ingredients.DB.status as ingredient_DB_status

import rich
	
from fractions import Fraction
import multiprocessing
import subprocess
import time
import os
import atexit

def foreground (script):
	the_process = subprocess.Popen (script)
	atexit.register (lambda: the_process.terminate ())
	time.sleep (5)
	
	return the_process
	
def background (script):
	the_process = subprocess.Popen (script)
	#time.sleep (5)
	return the_process

def on (
	apoplast_variables = {}
):
	status = ingredient_DB_status.status (
		apoplast_variables = apoplast_variables
	)
	if (status == "on"):
		print ("The moon is already on")
		return;

	port = apoplast_variables ["moon"] ["port"]
	dbpath = apoplast_variables ["moon"] ["path"]
	PID_path = apoplast_variables ["moon"] ["PID_path"]
	logs_path = apoplast_variables ["moon"] ["logs_path"]

	os.makedirs (dbpath, exist_ok = True)
	os.makedirs (
		os.path.dirname (PID_path), 
		exist_ok = True
	)

	script = [
		"mongod", 

		'--fork',

		'--dbpath', 
		#f"'{ dbpath }'", 
		f"{ dbpath }", 
		
		'--logpath',
		f"{ logs_path }", 
	
		
		'--port', 
		str (port),
		
		'--bind_ip',
		'0.0.0.0',
		
		'--pidfilepath',
		str (PID_path)
	]


	rich.print_json (data ={
		"procedure": script
	})

	#mongo_process = foreground (script)
	mongo_process = background (script)

	#mongo_process = multiprocessing.Process (target = open_process)
	#mongo_process.start ()

	status = ingredient_DB_status.status (
		apoplast_variables = apoplast_variables,
		loop_limit = 5
	)
	if (status == "on"):
		print ("The moon is already on")
		return mongo_process

	raise Exception ("A connection to the moon could not be established.")