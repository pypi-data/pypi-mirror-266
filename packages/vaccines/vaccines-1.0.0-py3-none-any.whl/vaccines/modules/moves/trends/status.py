

'''
	import vaccines.modules.moves.trends.status as trends_status
	the_status = trends_status.check_status ()
	
	
	# "on" or "off"
'''


from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import vaccines.climate as vaccines_climate
	
def check_status ():
	try:
		mongo = vaccines_climate.connect ()
		mongo.admin.command ('ismaster')
		print("Mongo is on.")
		
		return "on"
		
	except ConnectionFailure:
		pass;
	
	print ("A connection to mongo could not be established.")
	
	return "off"
