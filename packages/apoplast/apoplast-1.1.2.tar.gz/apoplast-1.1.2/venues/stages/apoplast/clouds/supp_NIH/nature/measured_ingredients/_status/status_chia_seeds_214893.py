

'''
	status_chia_seeds_214893
'''
'''
	python3 insurance.py clouds/supp_NIH/nature/measured_ingredients/_status/status_chia_seeds_214893.py
'''

import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
import apoplast.clouds.supp_NIH.examples as NIH_examples
import apoplast.clouds.supp_NIH.nature.measured_ingredients.seek_name as seek_name

import json

def check_1 ():	
	supp_NIH_example = NIH_examples.retrieve ("other/chia_seeds_214893.JSON")
	measured_ingredients = supp_NIH_nature.create (
		supp_NIH_example,
		return_measured_ingredients_grove = True
	)
	
	#print (json.dumps (measured_ingredients, indent = 4))
	
	measured_ingredient = seek_name.beautifully (
		measured_ingredients,
		name = "Phosphorus"
	)
	
	print (json.dumps (measured_ingredient, indent = 4))
	

	
	return;
	
checks = {
	"check 1": check_1
}