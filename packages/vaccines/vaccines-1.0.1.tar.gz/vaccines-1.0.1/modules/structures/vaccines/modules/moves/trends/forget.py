
'''
	itinerary:
		steps:
			find pass
			find and remote zip
			delete pass
'''


import vaccines.climate as vaccines_climate

from .zips.forget import forget_zip

from bson import ObjectId

def forget (
	id = None,
	delete_if_file_gone = False
):
	#
	#	if delete if file is gone, then proceed through zip forget
	#
	proceed_if_not_found = delete_if_file_gone

	mongo = vaccines_climate.link ()
	found = mongo.find_one ({
		'_id': ObjectId (id)
	})
	
	assert found is not None, f"""
	
	_id: { id } was not found.
	
	"""
	
	
	assert isinstance (found, dict), """
	
	_id: { id } document is not a dictionary.
	
	"""
	
	
	if ('zip' in found):
		zip_id = str (found ['zip'])
		print ("zip_id:", zip_id)	
		
		proceeds = forget_zip (
			found ['zip'],
			proceed_if_not_found = proceed_if_not_found
		)

	
	
	deletions = mongo.delete_one ({
		'_id': ObjectId (id)
	})
	print ("deletion count:", deletions.deleted_count)
	
	assert (deletions.deleted_count == 1), f'''
	
	exception: deletion count was: { deletions.deleted_count }
	
	'''
	
	assert (
		mongo.find_one ({
			'_id': ObjectId (id)
		}) == None
	)
	
	print (f"pass _id { id } was deleted.")
