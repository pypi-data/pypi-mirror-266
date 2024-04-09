


import os
import vaccines.climate as vaccines_climate


def turn_off ():
	mongo_climate = vaccines_climate.find ("mongo")
	PID_file_path = mongo_climate ["PID_file_path"]

	with open (PID_file_path, "r") as f:
		pid = int (f.read ().strip ())

	try:
		os.kill(pid, 15)
		print ("Mongo is off.")
		return;
		
	except OSError as e:
		print (f"Failed to stop Mongo: {e}")
		
	print ("An exception occurred")


