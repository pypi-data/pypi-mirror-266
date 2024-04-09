
import pathlib
import inspect
import os
from os.path import dirname, join, normpath

from vaccines._coms.clique_pro import clique


#import vaccines.config.scan as config_scan
import vaccines.climate as vaccines_climate
import vaccines.climate.moves.scan_config as config_scan

print ("vaccines @:", pathlib.Path (__file__).parent.resolve ())

configured = False

import rich

def is_configured ():
	return configured

def start ():
	vaccines_config = config_scan.start ()
	if (vaccines_config == False): 
		#print ("vaccines_config == False")
		
		print ("The config was not found; exiting.")
		print ()
		
		exit ();
		
		return;

	print ()
	print ("configuring")
	print ()
	
	print ('merging config', vaccines_config)
	vaccines_climate.merge_config (vaccines_config ["configuration"])
	
	
	rich.print_json (data = vaccines_climate.climate)
	rich.print_json (data = vaccines_climate.climate)
	
	
	return;


	'''
	rich.print_json (data = {
		"vaccines_config": vaccines_config
	})
	'''
	
	'''
	vaccines_climate.change ("mongo", {
		"directory": ""
	})
	'''
	
	'''
		get the absolute paths
	'''
	'''
	vaccines_config ["configuration"] ["treasuries"] ["path"] = (
		normpath (join (
			vaccines_config ["directory_path"], 
			vaccines_config ["configuration"] ["treasuries"] ["path"]
		))
	)
	'''
	
	
	'''
		paths:
			trends
				mongo_data_1
	
	
		mongo:
			safety
				passes
				zips
				zips.files
	'''
	trends_path = normpath (join (
		vaccines_config ["directory_path"], 
		vaccines_config ["configuration"] ["trends"] ["path"]
	))
	edited_config = {
		"mints": {
			"path": normpath (join (
				vaccines_config ["directory_path"], 
				vaccines_config ["configuration"] ["mints"] ["path"]
			))
		},
		"trends": {
			"path": trends_path,
			
			"nodes": [{
				"host": "localhost",
				"port": "27017",
				"data path": normpath (join (
					trends_path, 
					"mongo_data_1"
				))
			}]
		},
		"CWD": vaccines_config ["directory_path"]
	}
	
	'''
	config_template = {
		
	}
	'''
	
	rich.print_json (data = {
		"edited_config": edited_config
	})

	
	vaccines_climate.change ("edited_config", edited_config)
	

	#print ('vaccines configuration', vaccines_config.configuration)

	'''
		Add the changed version of the basal config
		to the climate.
	'''
	'''
	config = vaccines_config ["configuration"];
	for field in config: 
		vaccines_climate.change (field, config [field])
	'''
	
	configured = True
	
	print ()
