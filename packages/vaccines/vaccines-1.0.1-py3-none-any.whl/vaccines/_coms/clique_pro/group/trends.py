


import vaccines.modules.moves.trends_to_mint as trends_to_mint

import vaccines.modules.moves.trends.find as find_trend
import vaccines.modules.moves.trends.forget as forget_trend
import vaccines.modules.moves.trends.on as on
import vaccines.modules.moves.trends.off as off
import vaccines.modules.moves.trends.status as status

import vaccines.modules.moves.trends.show as show_trends

import click

def add ():
	
	@click.group ("trends")
	def group ():
		pass

	@group.command ("data-save")
	def export_data ():
		print ("data-save is not implemented.")
		
		'''
			mongodump --db safety --out=safety_1 --uri="mongodb://localhost:27017/"
		'''
		
	@group.command ("data-restore")
	def export_data ():
		print ("data-restore is not implemented.")
		
		'''
			#
			#	opening as same database?
			#
		
			#
			#	opening as a different database?
			#
			mongorestore safety_1 --nsFrom='safety.*' --nsTo='safety_2.*' --uri="mongodb://localhost:27017/"
		'''

	@group.command ("turn-on")
	def turn_on ():
		on.turn_on ()
	
	@group.command ("turn-off")
	def turn_off ():
		off.turn_off ()
		
	@group.command ("status")
	def turn_off ():
		status.check_status ()

	@group.command ("find")
	@click.option ('--name', required = True)
	def search (name):
		find_trend.find (name = name)
	
	@group.command ("list")
	def list_ ():
		show_trends.show ()
	
	@group.command ("show")
	def show ():
		show_trends.show ()
	
	@group.command ("forget")
	@click.option ('--id', required = True)
	@click.option ('--delete-if-file-gone', is_flag = True, default = False)
	def forget (id, delete_if_file_gone):		
		forget_trend.forget (
			id = id,
			delete_if_file_gone = delete_if_file_gone
		)
		

	'''
		vaccines trends to-mints --name folder
	'''
	@group.command ("to-mints")
	@click.option ('--name', required = True)
	@click.option ('--id', required = False, default = '')
	def retrieve_command (name, id):
		trends_to_mint.start (
			name = name,
			id = id
		)

	return group




#



