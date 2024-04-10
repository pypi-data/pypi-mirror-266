

'''
	mongod --shutdown --pidfilepath /var/run/mongodb/mongod.pid
'''

import multiprocessing
import subprocess
import time
import os
import atexit

def background (script):
	print (script)

	return subprocess.Popen (script)

def off (
	apoplast_variables = {}
):
	port = apoplast_variables ["moon"] ["port"]
	dbpath = apoplast_variables ["moon"] ["path"]
	PID_path = apoplast_variables ["moon"] ["PID_path"]
	logs_path = apoplast_variables ["moon"] ["logs_path"]
	
	
	
	mongo_process = background ([
		"mongod",
		"--shutdown",
		
		'--dbpath', 
		f"{ dbpath }", 
		
		"--pidfilepath",
		f"'{ PID_path }'"
	])
	
	
	
	
	
	
	return;