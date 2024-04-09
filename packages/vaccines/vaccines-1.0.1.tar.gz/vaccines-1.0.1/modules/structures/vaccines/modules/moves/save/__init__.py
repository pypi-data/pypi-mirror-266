
'''
	itinerary:
		steps:
			

'''


'''
	import vaccines.modules.moves.save as save
	save.save ()
'''

import pymongo
from gridfs import GridFS
import pathlib
from os.path import dirname, join, normpath
import os

import vaccines.climate as climate
from .modules.zip_and_save_to_gridfs import zip_and_save_to_gridfs

def save (
	name = ''
):
	edited_config = climate.find ("edited_config")

	id = zip_and_save_to_gridfs (
		name = name,
		directory_path = str (normpath (join (edited_config ["mints"] ["path"], name))), 
		
		metadata = None
	)

	proceeds = climate.link ().insert_one ({
		"legal": {
			"name": name,
			"tags": [],
			"locks": [] 
		},
		"zip": id
	})
	print ("added pass _id:", proceeds.inserted_id)
	
	'''
		Figure out is inserted.
	'''
	found = climate.link ().find_one({ "_id": proceeds.inserted_id })
	assert (
		str (found ["_id"]) == str (proceeds.inserted_id)
	), [ str (found ["_id"]), str (proceeds.inserted_id)]
	
