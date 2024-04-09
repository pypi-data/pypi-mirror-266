





'''
	import vaccines.climate.scan as vaccines_climate_scan
	vaccines_ganglia = vaccines_climate_scan.start ("vaccines ganglia")
'''




import pathlib
from os.path import dirname, join, normpath
import sys
import copy
import json
import os.path
import inspect
import os

import ships.paths.files.scan.JSON as scan_JSON_path

'''
	if current directory is /1/1/1/1/1/
	
	looks in each directory for a vaccines.JSON file
	
	possibilities:
		vaccines.yaml
'''

name = "vaccines.JSON"

def start ():
	#search_directory = os.path.abspath ((inspect.stack()[2])[1])
	#print ("search_directory:", search_directory)

	search_directory = os.getcwd ()
	
	searched = []
	while (search_directory != "/"):
		search_file_path = normpath (join (search_directory, name))
		print ("searching:", search_file_path)
		
		vaccines_JSON_exists = os.path.isfile (search_file_path) 
		if (vaccines_JSON_exists):
			print ("vaccines.JSON found:", search_file_path)
		
			return {
				"configuration": scan_JSON_path.start (search_file_path),
				"file_path": search_file_path,
				"directory_path": search_directory
			}
		
		searched.append (search_file_path)
	
		search_directory = os.path.dirname (search_directory)
		
	 
	
	print (f"""
		
A "vaccines.JSON" file was not found.
		
These paths were searched: { json.dumps (searched, indent = 4) }
		
	""")
	
	return False;
