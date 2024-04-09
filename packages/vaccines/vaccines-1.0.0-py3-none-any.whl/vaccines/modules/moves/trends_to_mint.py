








import pymongo
from bson import json_util
from bson.objectid import ObjectId

from gridfs import GridFS
import pathlib
from os.path import dirname, join, normpath
import os

import vaccines.climate as vaccines_climate
import rich

import zipfile
import io


def unzip (
	file_content,
	extraction_directory_path
):
	with zipfile.ZipFile(io.BytesIO (file_content)) as zip_file:
		zip_file.extractall (extraction_directory_path)
		print("File unzipped successfully.")
		

def unzip_directory (
	GridFS_collection,
	zip_id = "",
	extraction_directory_path = ""
):
	rich.print_json (data = {
		"unzipping": {
			"zip id": str (zip_id),
			"extraction path": extraction_directory_path
		}
	})
	
	if (os.path.exists (extraction_directory_path)):
		print (f"Something is already at: '{ extraction_directory_path }'")
		return;
	

	#fs = GridFS_zip_files_driver

	# Specify the ObjectId of the file you want to retrieve
	file_id = ObjectId (zip_id)

	file_obj = GridFS_collection.find_one ({
		"_id": ObjectId (zip_id)
	})
	
	print ("file obj", file_obj)
	
	file_content = file_obj.read ()

	unzip (
		file_content,
		extraction_directory_path
	)

	return;
	'''
	# Retrieve the file from GridFS
	file_doc = fs.find_one({"_id": file_id})
	if file_doc:
		file_data = fs.chunks.find ({ 
			"files_id": file_id
		}).sort([
			("n", 1)
		])
		
		#file_data = db.fs.chunks.find({"files_id": file_id}).sort([("n", 1)])
		file_content = b"".join(chunk ["data"] for chunk in file_data)

		print ("file_content:", file_content)

		# Unzip the file content
		with zipfile.ZipFile(io.BytesIO (file_content)) as zip_file:
			zip_file.extractall (extraction_directory_path)
			print("File unzipped successfully.")
	else:
		print("File not found.")

	print ("unzipped?")
	'''

def start (
	name = '',
	id = ''
):
	print ('id:', id)

	climate_mongo = vaccines_climate.find ("mongo")

	print ("climate_mongo", climate_mongo)
	
	DB_name = climate_mongo ["DB_name"]
	DB_collection_zips = climate_mongo ["passes"] ['GridFS_zips']
	DB_collection_zips_files = climate_mongo ["passes"] ['GridFS_zips_files']
	mongo_connection = climate_mongo ["connection"]

	mongo_client = pymongo.MongoClient (mongo_connection)
	

	
	mongo_DB = mongo_client [ DB_name ]
	GridFS_collection = GridFS (mongo_DB, collection = DB_collection_zips)
	GridFS_collection_files = mongo_DB [ DB_collection_zips_files ]

	if (len (id) == 0):
		proceeds = mongo_DB ["passes"].find ({
			"legal.name": name
		})

		documents = []
		for proceed in proceeds:
			documents.append ({
				"_id": str (proceed ["_id"]),
				"zip": str (proceed ["zip"]),
				"legal": proceed ["legal"]
			})
			
		if (len (documents) == 1):
			unzip_directory (
				GridFS_zip_files_driver = GridFS_collection_files,
				_id = documents [0] ["_id"],
				extraction_directory_path = str (normpath (join (os.getcwd (), name)))
			)
		
			return documents [0]		
		
		rich.print_json (data = documents)
		return;
			
	
	print ("searching", id)
	
	found = mongo_DB ["passes"].find_one ({
		"_id": ObjectId (id)
	})
	
	print (found)
		
	unzip_directory (
		GridFS_collection = GridFS_collection,
		zip_id = found ["zip"],
		extraction_directory_path = str (normpath (join (os.getcwd (), name)))
	)
		
	


	#
