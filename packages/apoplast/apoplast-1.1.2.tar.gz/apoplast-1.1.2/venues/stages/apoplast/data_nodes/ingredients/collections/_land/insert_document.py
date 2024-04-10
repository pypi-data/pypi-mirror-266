
'''
	import apoplast.data_nodes.ingredients.collections._land.insert_document as _land_insert_document
	_land_insert_document.smoothly (
		collection,
		document = {},
		
		add_region = True
	)
'''

'''
	itinerary:
		https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
		
		region = highest region number + 1
'''

def smoothly (
	collection = None,
	document = {},
	
	add_region = False
):
	if (add_region):
		result = list (
			collection.aggregate ([
				{
					"$group": {
						"_id": None, 
						"max_region": {
							"$max": "$region"
						}
					}
				}
			])
		)
		region = result[0]['max_region'] + 1 if result else 1
		
		print ('region:', region)
		
		return collection.insert_one ({
			** document,
			"region": region
		})
		

	return collection.insert_one (document)
