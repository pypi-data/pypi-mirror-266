

'''
	mongod --dbpath ./../_mongo_data --port 39000
'''

'''
	import apoplast.data_nodes.ingredients.DB.status as ingredient_DB_status
	status = ingredient_DB_status.status (
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

from fractions import Fraction
import multiprocessing
import subprocess
import time
import os
import atexit

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

from apoplast._variables import receive_moon_URL


import ships.cycle as cycle

def status (
	apoplast_variables = {},
	loop_limit = 1
):
	moon_URL = receive_moon_URL (
		apoplast_variables = apoplast_variables
	)
	
	print ("searching URL:", moon_URL)	
	
	counter = 0
	
	def show (* positionals, ** keywords):
		nonlocal counter
		counter += 1
	
		print (f'connection attempt { counter }', positionals, keywords)
	
		try:
			client = MongoClient (moon_URL, serverSelectionTimeoutMS=2000)
			
			print ('	client:', client)
			
			client.server_info ()
			print ("	A connection to the moon was established!")
			
			return "on"
			
		except ConnectionFailure:
			pass;
			
		print ("	A connection to the moon could not be established!\n")
		
		if (counter == loop_limit):
			return "off"
		
		raise Exception ("")
		
	
	proceeds = cycle.loops (
		show, 
		cycle.presents ([ 1 ]),
		
		#
		#	this is the loop limit
		#
		loops = loop_limit,
		delay = Fraction (1, 1),
		
		records = 0
	)
	
	print ("The moon is:", proceeds)
	
	
	return proceeds;

	
