



from apoplast.data_nodes.clique import clique as data_nodes_clique

from .group import clique as clique_group
import click

def clique ():
	@click.group ()
	def group ():
		pass

	@click.command ("example")
	def example_command ():	
		print ("example")

	group.add_command (example_command)
	
	group.add_command (clique_group ())
	group.add_command (data_nodes_clique ())
	
	group ()




#
