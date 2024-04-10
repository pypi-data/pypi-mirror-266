
'''
	import apoplast.measures.number.sci_note_2 as sci_note_2
	sci_note_number = sci_note_2.produce ('9999999')
'''

import numpy
from fractions import Fraction

def produce (the_fraction_string):
	return numpy.format_float_scientific (
		numpy.float32 (Fraction (the_fraction_string)), 
		unique = True, 
		min_digits = 4, 
		precision = 4, 
		exp_digits = 1
	)