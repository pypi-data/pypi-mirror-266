
'''
	can save and retrieve a mint
'''

import vaccines
import vaccines.climate as vaccines_climate

import vaccines.modules.moves.trends.status as trends_status
	
def check_1 ():
	the_show = vaccines_climate.find ("the_show")

	print ("the_show:", the_show)
	
	vaccines.start ()
	the_status = trends_status.check_status ()
	print ("the_status:", the_status)

	return;
	
	
checks = {
	'check 1': check_1
}