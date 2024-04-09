

'''
	#
	#	change
	#
	import vaccines.climate as vaccines_climate
	vaccines_climate.change ("treasuries", {
		"path": treasuries_path
	})
	
	vaccines_climate.change ("mongo", {
		"directory": ""
	})
'''


'''
	#
	#	find
	#
	import vaccines.climate as vaccines_climate
	mongo_climate = vaccines_climate.find ("mongo")
'''

'''

'''

import copy
import pydash

import pathlib
from os.path import dirname, join, normpath
import sys
def the_show_path ():
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	the_vaccines_process = str (normpath (join (this_directory, "../__bin/vaccines_1")))
	
	return the_vaccines_process

climate = {
	"the_show": the_show_path (),
	
	#
	#	trends
	#		node_1
	#			mongo_data
	#			mongod.pid
	#			logs.log
	#
	"trends": {
		"path": "trends",
		
		"mongo": {
			"nodes": [{
				"rel_path": "node_1",
				
				"host": "localhost",
				"port": "27017",
				
				"PID_file_name": "mongod.pid",
				"log_file_name": "logs.log",
			}], 

			"DB_name": 'safety',
			"passes": {
				"collection": "passes",
				"GridFS_zips": 'zips',
				"GridFS_zips_files": 'zips.files'
			}
		}	
	}
}


'''
	import climate
	mongo = climate.connect ()
'''
from pymongo import MongoClient
import gridfs
def connect ():
	edited_config = find ("edited_config")
	
	nodes = edited_config ["trends"] ["nodes"]
	node_1 = nodes [0]
	
	host = node_1 ["host"]
	port = node_1 ["port"]

	mongo = MongoClient (f'mongodb://{ host }:{ port }/')
	
	return mongo;
	
def link ():
	return connect () ["safety"] ["passes"]


'''
	import vaccines.climate as climate
	GridFS = climate.link_FS ()
'''
def link_FS ():
	the_connection = connect ();
	DB = the_connection ["safety"]
	
	return gridfs.GridFS (DB, collection = "zips")

def link_FS_files ():
	the_connection = connect ();
	return the_connection ["safety"] ["zips.files"]


def change (field, plant):
	climate [ field ] = plant


'''
	import vaccines.climate as climate
	climate.change_nested ("mongo.PID_file_path", "")
	climate.change_nested ("mongo.log_file_path", "")
	climate.change_nested ("mongo.connection", "")
'''
def change_nested (field_path, field_plant):
	pydash.set_ (climate, field_path, field_plant)


'''
	import vaccines.climate as vaccines_climate
	vaccines_climate.merge_config (config)
'''
def merge_config (config):
	global climate
	climate = pydash.merge_with (
		climate, 
		config
	)


'''
	import vaccines.climate as climate
	climate.find_nested ("trends.mongo.PID_file_path", "")
'''
def find_nested (field_path, field_plant):
	return copy.deepcopy (
		pydash.get (climate, field_path, field_plant)
	)

def find (field):
	return copy.deepcopy (climate) [ field ]