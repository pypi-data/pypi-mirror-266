


import click

def clique ():
	
	@click.group ("treasuries")
	def group ():
		pass

	'''
		vaccines treasuries names
	'''
	@group.command ("names")
	def names ():
		import vaccines.treasuries.names as treasuries_names
		names = treasuries_names.start ()
	
		for name in names:
			print (name)
	
	
	'''
		vaccines treasuries definitions --name "hacienda"
	'''
	@group.command ("definitions")
	@click.option ('--name', required = True)
	def names (name):
		import vaccines.treasuries.names as treasuries_names
		found_name = treasuries_names.start (
			find_name = name
		)
	
		print ('found:', found_name)
	
	

	@group.command ("enumerate")
	#@click.option ('--example-option', required = True)
	def search ():
		#print ("example_option:", example_option)
	
		return;

	return group




#



