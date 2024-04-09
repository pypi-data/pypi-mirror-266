


'''
	import vaccines.mints.names as mints_names
	mints_names = mints_names.start ()
'''

import vaccines.climate as vaccines_climate
from pathlib import Path

import os

def start ():	
	mints = vaccines_climate.find ("edited_config") ["mints"]	
	mints_path = mints ['path']
	
	directory_names = []
	for trail in Path (mints_path).iterdir ():
		name = os.path.relpath (trail, mints_path)
		
		if trail.is_dir ():
			directory_names.append (name)
	
		else:
			raise Exception (f'found a path that is not a directory: \n\n\t{ name }\n')
		
	
		'''
		if trail.is_file ():
			print(f"{trail.name}:\n{trail.read_text()}\n")
		'''
		
	return directory_names;