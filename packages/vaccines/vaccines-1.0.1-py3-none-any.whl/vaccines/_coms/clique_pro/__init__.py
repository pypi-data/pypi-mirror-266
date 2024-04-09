




#from .group import clique as clique_group






import click

import vaccines
import vaccines._coms.clique_pro.group.trends as trends_group
import vaccines.modules.moves.save as save

from vaccines.mints import clique as mints_group
from vaccines.treasuries import clique as treasuries_group

def clique ():
	'''
		This configures the vaccines module.
	'''
	vaccines.start ()

	@click.group ()
	def group ():
		pass
	
	@group.command ("help")
	def help ():
		import pathlib
		from os.path import dirname, join, normpath
		this_directory = pathlib.Path (__file__).parent.resolve ()
		this_module = str (normpath (join (this_directory, "..")))

		import somatic
		somatic.start ({
			"directory": this_module,
			"extension": ".s.HTML",
			"relative path": this_module
		})
		
		import time
		while True:
			time.sleep (1)

	



	group.add_command (mints_group.clique ())
	#group.add_command (treasuries_group.clique ())
	
	group.add_command (trends_group.add ())
	
	group ()




#
