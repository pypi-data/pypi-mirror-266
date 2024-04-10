




from apoplast.data_nodes.ingredients.clique import clique as ingredients_clique

def clique ():
	import click
	@click.group ("data_node")
	def group ():
		pass

	group.add_command (ingredients_clique ())

	return group




#



