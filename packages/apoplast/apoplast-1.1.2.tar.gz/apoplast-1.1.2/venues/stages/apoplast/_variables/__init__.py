

'''
	from apoplast._variables import prepare_variables
	apoplast_variables = prepare_variables ({
		"moon": {
			"name": "apoplast ingredients",
			"port": "39001"
		}
	})
'''

'''
# receive_moon_URL
from apoplast._variables import receive_moon_URL
moon_URL = receive_moon_URL (
	apoplast_variables = apoplast_variables
)
'''

import pathlib
from os.path import dirname, join, normpath
import sys

import pydash

def receive_moon_URL (
	apoplast_variables = {}
):
	return "mongodb://" + apoplast_variables ["moon"] ["host"] + ":" + apoplast_variables ["moon"] ["port"] + "/"

def prepare_variables (
	variables = {}
):
	this_folder = pathlib.Path (__file__).parent.resolve ()	

	return pydash.merge (
		{
			"moon": {
				#"URL": "mongodb://localhost:39000/",
				
				"host": "0.0.0.0",
				"port": "39000",
				"DB_name": "ingredients",
				"path": str (normpath (join (this_folder, "../data_nodes/ingredients/_data"))),
				
				"PID_path": "/procedures/apoplast/moon/mongo.pid",
				"logs_path": "/procedures/apoplast/moon/mongo.logs",
			},
			"harbor": {
				"path": str (normpath (join (this_folder, "../_interfaces/sanic/__init__.py"))),
				
				"PID_path": "/procedures/apoplast/harbor/harbor.pid"
			}
			
		},
		variables
	)