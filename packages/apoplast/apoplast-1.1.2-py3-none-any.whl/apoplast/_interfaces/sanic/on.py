

'''
	python3 --shutdown --pidfilepath /var/run/mongodb/mongod.pid
'''

import multiprocessing
import subprocess
import time
import os
import atexit

def background (script):
	return subprocess.Popen (script)

def off (
	apoplast_variables = {}
):
	port = apoplast_variables ["moon"] ["port"]
	PID_path = apoplast_variables ["moon"] ["PID_path"]
	
	mongo_process = background ([
		"python3",
		"--shutdown",
		
		'--dbpath', 
		f"{ dbpath }", 
		
		"--pidfilepath",
		f"'{ PID_path }'"
	])

	return;