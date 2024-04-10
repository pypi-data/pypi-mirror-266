
'''
	import apoplast.data_nodes.ingredients.DB.connect as connect_to_ingredient
	ingredients_DB = connect_to_ingredient.DB (
		apoplast_variables = apoplast_variables
	)
'''

from apoplast._variables import receive_moon_URL


import pymongo

def DB (
	apoplast_variables = {}
):
	# URL = apoplast_variables ["moon"] ["URL"]
	
	moon_URL = receive_moon_URL (
		apoplast_variables = apoplast_variables
	)
	
	DB_name = apoplast_variables ["moon"] ["DB_name"]

	mongo_connection = pymongo.MongoClient (moon_URL)
	DB = mongo_connection [ DB_name ]

	return DB