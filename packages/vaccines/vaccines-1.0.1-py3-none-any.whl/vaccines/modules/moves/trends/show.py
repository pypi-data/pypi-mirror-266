

import rich

import vaccines.climate as vaccines_climate

def show ():
	mongo = vaccines_climate.connect ()


	documents = mongo ['safety'] ['passes'].find ()

	# Iterate over the documents and print them
	data = []
	for document in documents:	
		data.append ({
			"_id": str (document ["_id"]),
			"legal": document ["legal"]
		})

	rich.print_json (data = data)