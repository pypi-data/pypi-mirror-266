
'''
	python3 insurance.py clouds/supp_NIH/nature/measured_ingredient/_status/status_1.py
'''

import apoplast.clouds.supp_NIH.nature.measured_ingredient as measured_ingredient_builder

import rich

def check_1 ():
	'''
		454
	'''
	measured_ingredient = measured_ingredient_builder.build (
		form = {
            "unit": "gram",
            "amount per package": "454",
            "serving size amount": "12",
            "amount is an estimate": "yes"
        },
		NIH_ingredient = {
			"order": 19,
			"ingredientId": 281043,
			"description": "",
			"notes": "",
			"quantity": [
				{
					"servingSizeOrder": 1,
					"servingSizeQuantity": 12,
					"operator": "=",
					"quantity": 75.7,
					"unit": "mg",
					"dailyValueTargetGroup": [
						{
							"name": "Adults and children 4 or more years of age",
							"operator": "=",
							"percent": 6,
							"footnote": None
						}
					],
					"servingSizeUnit": "Gram(s)"
				}
			],
			"nestedRows": [],
			"name": "Calcium",
			"category": "mineral",
			"ingredientGroup": "Calcium",
			"uniiCode": "SY7Q814VUP",
			"alternateNames": [
				"Ca"
			],
			"forms": []
		}
	)

	rich.print_json (data = measured_ingredient)
	
	'''
		2.8639833333333335 grams 
			= (.0757 / 12) * 454
	'''
	assert (
		measured_ingredient ["measures"] ["mass + mass equivalents"] ["per form"] ["grams"] ["fraction string"] ==
		"355127595616611/56294995342131200"
	)
	
	'''
		0.006 grams?
			(.0757 / 12) = 0.006308333333333334
	'''
	assert (
		measured_ingredient ["measures"] ["mass + mass equivalents"] ["per package"] ["grams"] ["fraction string"] ==
		"80613964204970697/28147497671065600"
	)



	return;
	
	
checks = {
	'check 1': check_1
}