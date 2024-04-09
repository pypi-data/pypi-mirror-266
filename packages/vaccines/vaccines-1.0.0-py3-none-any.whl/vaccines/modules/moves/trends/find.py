


import vaccines.climate as climate
import rich


def find (
	name = ""
):
	mongo = climate.link ()
	documents = mongo.find ({
		'legal.name': name
	})
	
	#print ("name:", name)
	#print ("documents:", documents)
	
	data = []
	for document in documents:	
		data.append ({
			"_id": str (document ["_id"]),
			"legal": document ["legal"]
		})

	rich.print_json (data = data)