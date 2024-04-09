





import io
import zipfile
import pymongo
from gridfs import GridFS
import os
import shutil
import tempfile
'''
	from vaccines.modules.freight.save import zip_and_save_to_gridfs
	zip_and_save_to_gridfs (
		directory_path = str (normpath (join (this_directory, 'folder'))), 
		metadata = None,
		
		GridFS_driver = None,
		GridFS_collection_files = None
	)
'''

def zip_shutil_temp (directory_path):
	with tempfile.TemporaryDirectory() as temp_dir:
		temp_zip_path = os.path.join (temp_dir, 'temp_zipfile.zip')

		shutil.make_archive (temp_zip_path[:-4], 'zip', directory_path)

		# Read the zip file into memory if needed
		with open (temp_zip_path, 'rb') as zip_file:
			#zip_data = zip_file.read ()
			zip_data = io.BytesIO (zip_file.read ())

	return zip_data

def zip_walk (directory_path):
	zip_buffer = io.BytesIO ()
	with zipfile.ZipFile (zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for root, dirs, files in os.walk (directory_path):
			for file in files:
				file_path = os.path.join (root, file)
				zipf.write (
					file_path, 
					os.path.relpath (file_path, directory_path)
				)
				
	zip_buffer.seek (0)

	return zip_buffer

import vaccines.climate as climate
import vaccines.modules.moves.trends.extract_to_temp as extract_to_temp
import rich
def zip_and_save_to_gridfs (
	directory_path, 
	name = 'unnamed_archive',
	
	metadata = {}
):
	rich.print_json (data = {
		"directory_path": directory_path,
		"name": name
	})

	zip_buffer = zip_shutil_temp (directory_path)

	GridFS = climate.link_FS ()
	GridFS_files = climate.link_FS_files ()

	zip_id = GridFS.put (
		zip_buffer, 
		filename = name + '.zip', 
		metadata = metadata
	)
	print ("Added zip id:", zip_id)
	
	GridFS_files.update_one (
		{'_id': zip_id }, 
		{'$set': {'uploadDate': '' }}
	)
	print ("Modified id:", zip_id)
	
	
	extract_to_temp.extract (
		zip_id,
		original_directory_path = directory_path
	)
	
	
	return zip_id;




