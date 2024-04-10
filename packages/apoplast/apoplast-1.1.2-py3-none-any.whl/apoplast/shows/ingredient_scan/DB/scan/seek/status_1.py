




'''
	python3 status.proc.py shows/ingredient_scan/DB/scan/seek/status_1.py
'''


import apoplast.shows.ingredient_scan.DB.scan.seek as seek_nutrient
import apoplast.insure.equality as equality

def check_1 ():	
	nutrient = seek_nutrient.presently (
		for_each = lambda essential : True if "thiamin" in essential ["names"] else False
	)
	
	equality.check ("thiamin" in nutrient ["names"], True)
	equality.check ("thiamine" in nutrient ["names"], True)
	equality.check ("vitamin b1" in nutrient ["names"], True)
	
def check_2 ():	
	nutrient = seek_nutrient.presently (
		for_each = lambda essential : True if essential ["region"] == 1 else False
	)
	
	equality.check ("protein" in nutrient ["names"], True)	

def check_3 ():	
	ingredient = "ThiamIn"

	def for_each (essential):
		for name in essential ["names"]:
			if (name.lower () == ingredient.lower ()):
				return True;
			
		return False

	nutrient = seek_nutrient.presently (
		for_each = for_each
	)
	
	assert ("thiamin" in nutrient ["names"])
	assert (nutrient ["region"] == 66)

checks = {
	'seek name': check_1,
	'seek region': check_2,
	'seek name 2': check_3
}