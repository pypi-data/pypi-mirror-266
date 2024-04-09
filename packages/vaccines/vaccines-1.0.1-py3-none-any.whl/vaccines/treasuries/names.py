


'''
	import vaccines.ganglia.list as vaccines_ganglia_list
	vaccines_ganglia_list.start ()
'''


'''
	[{
		"name": "",
		"definitions": []
	}]
'''

import vaccines.climate as vaccines_climate
from pathlib import Path

import os
from rich import print_json

def start (
	find_name = None,
	return_multiple = False
):	
	treasuries = vaccines_climate.find ("treasuries")	
	treasuries_path = treasuries ['path']
	
	issues = []
	
	proceeds = []
	
	directory_names = []
	for address in Path (treasuries_path).iterdir ():
		address_name = os.path.relpath (address, treasuries_path)
		
		print ("address_name", address_name)
		
		proceed = {
			"name": address_name,
			"definitions": []
		}
		
		if address.is_dir ():
			for treasury_path in Path (address).iterdir ():
				if treasury_path.is_dir ():
					treasury_name = os.path.relpath (treasury_path, address)
					treasury_name_split = treasury_name.split ('.')
					
					last_index_of_treasury = len (treasury_name_split) - 1;
					treasury_definition_number = int (treasury_name_split [ last_index_of_treasury ])
					
					assert (type (treasury_definition_number) == int), treasury_path
					proceed ["definitions"].append (treasury_name)
					
					print (find_name, treasury_name)
					
					
					
				else:
					issues.append ({
						"exception": "This module address is not a directory.",
						"path": str (treasury_path)
					})
				
				
		else:
			issues.append ({
				"exception": "This address is not a directory.",
				"path": address
			})
		
			#raise Exception (f'found a path that is not a directory: \n\n\t{ name }\n')
		
		if (find_name == address_name):
			return proceed
		
		proceeds.append (proceed)
	
		'''
		if trail.is_file ():
			print(f"{trail.name}:\n{trail.read_text()}\n")
		'''
	
	if (len (issues) >= 1):
		print_json (data = issues)
		raise Exception (f"Issues were found with the vaccines directory.")
	
	if (type (find_name) == str):
		raise Exception (f"The name given was not found.")
	
	if (return_multiple):
		return {
			"proceeds": proceeds,
			"issues": issues
		}
	
	return proceeds