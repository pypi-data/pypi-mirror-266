


import io
import zipfile
import pymongo
from gridfs import GridFS
import os

'''
	from vaccines.modules.freight.save import zip_and_save_to_gridfs
	zip_and_save_to_gridfs (
		directory_path = str (normpath (join (this_directory, 'folder'))), 
		metadata = None,
		
		GridFS_driver = None,
		GridFS_collection_files = None
	)
'''
def zip_and_save_to_gridfs (
	directory_path, 
	name = 'unnamed_archive',
	
	metadata = {},
	
	GridFS_collection = None,
	GridFS_collection_files = None
):
	zip_buffer = io.BytesIO ()
	with zipfile.ZipFile (zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for root, dirs, files in os.walk (directory_path):
			for file in files:
				file_path = os.path.join(root, file)
				zipf.write (
					file_path, 
					os.path.relpath (file_path, directory_path)
				)

	zip_buffer.seek (0)

	id = GridFS_collection.put (
		zip_buffer, 
		filename = name + '.zip', 
		metadata = metadata
	)
	
	GridFS_collection_files.update_one (
		{'_id': id }, 
		{'$set': {'uploadDate': '' }}
	)
	
	print ("id:", id)
	return id;


