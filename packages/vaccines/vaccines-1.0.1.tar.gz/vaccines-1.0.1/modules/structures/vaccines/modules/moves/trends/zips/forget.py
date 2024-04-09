

from bson import ObjectId
import vaccines.climate as climate
	
def forget_zip (_id, proceed_if_not_found = False):
	GridFS = climate.link_FS ()
	
	#the_id = ObjectId ('_id');
	the_id = _id
	
	exists_before_deletion = GridFS.exists (the_id)
	if (not exists_before_deletion):
		if (proceed_if_not_found):
			return;
		
		
		the_exception = f'''
		
	zip { the_id } could not be found.	
		
	use this flag to proceed with deletion of the trend:
		--delete-if-file-gone
		
		'''
		
		
		raise Exception (the_exception)
	
	
	GridFS.delete (the_id)
	exists_after_deletion = GridFS.exists (the_id)
	assert (
		exists_after_deletion == False
	), "The zip couldn't be deleted for some reason."
	
	str_id = str (_id)
	print (f"zip { str_id } was deleted.")
