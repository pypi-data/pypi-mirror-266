


import apoplast.data_nodes.ingredients.DB.on as ingredient_DB_on
import apoplast.data_nodes.ingredients.DB.off as ingredient_DB_off
import apoplast.data_nodes.ingredients.DB.status as ingredient_DB_status

import apoplast.data_nodes.ingredients.DB.connect as connect_to_ingredient
from apoplast._variables import prepare_variables

def clique ():
	import click
	@click.group ("ingredients")
	def group ():
		pass


	import click
	@group.command ("on")
	#@click.option ('--example-option', required = True)
	def on ():
		print ("on")
		mongo_process = ingredient_DB_on.on (
			apoplast_variables = prepare_variables ({
				"moon": {}
			})
		)

	import click
	@group.command ("off")
	#@click.option ('--example-option', required = True)
	def off ():
		ingredient_DB_off.off (
			apoplast_variables = prepare_variables ({
				"moon": {}
			})
		)

	import click
	@group.command ("status")
	#@click.option ('--example-option', required = True)
	def off ():
		ingredient_DB_status.status (
			apoplast_variables = prepare_variables ({
				"moon": {}
			}),
			loop_limit = 3
		)
	

	return group




#



