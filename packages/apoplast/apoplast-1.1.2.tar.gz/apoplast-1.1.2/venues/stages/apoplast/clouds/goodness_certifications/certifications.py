


import rich

certifications = [
	{
		"certification": "VegeCert Certified Vegan",
		
		"domain": "vegecert.com" ,
		"kind": "yes",
		"links": [
			"https://vegecert.com/standards",
		],
		"show": {
			"text": "Vegecert Certified Vegan"
		}
	},

	{
		"certification": "BeVeg certified",
		
		"domain": "beveg.com" ,
		"kind": "yes",
		"links": [
			"https://www.beveg.com",
			"https://www.beveg.com/vegan-certification-process"
		] ,
		"show": {
			"text": "BeVeg certified"
		}

	},
	{
		"certification": "Vegan®" ,
		"domain": "vegansociety.com" ,
		"kind": "yes",
		"links": [
			"https://www.vegansociety.com/the-vegan-trademark",
			"https://www.vegansociety.com",
			"https://www.vegansociety.com/shop/veg-1-supplements"
		] ,
		"show": {
			"text": "Vegan®"
		}
	},
	{
		"certification": "vegan stamp on packaging",
		
		"description": "The packaging indicates that this product is vegan.",
		"domain": "" ,
		"kind": "yes" ,
		"links": [],
		"show": {
			"text": "vegan stamp on packaging"
		}
	},
	{
		"certification": "Vegetarian Society, Vegan Approved",
		
		"domain": "https://vegsoc.org",
		"kind": "yes",
		"links": [
			"https://vegsoc.org/vegetarian-and-vegan-approved-trademarks"
		],
		"show": {
			"text": "Vegetarian Society, Vegan Approved"
		}
	},
	{
		"certification": "Certified Plant Based",
		
		"domain": "plantbasedfoods.org",
		"kind": "yes",
		"links": [
			"https://www.plantbasedfoods.org/marketplace/certification"
		],
		"show": {
			"text": "Certified Plant Based"
		}
	},

	{
		"certification": "Certified Vegan Vegan.org" ,
		
		"domain": "vegan.org",
		"kind": "yes",
		"links": [
			"vegan.org",
			"https://vegan.org/certification-alerts"
		],
		"show": {
			"text": "Certified Vegan Vegan.org"
		}
	} 
]

rich.print_json (data = certifications)