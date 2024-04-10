

'''
	python3 status.proc.py "measures/number/sci_note_2/status_1.py"
'''

import apoplast.measures.number.sci_note_2 as sci_note_2
from fractions import Fraction

def equal (s1, s2):
	s1_ = sci_note_2.produce (s1)
	assert (s1_ == s2), [ s1, s1_, s2 ]


def status_1 ():	
	equal ('9999999', "1.0000e+7")	
	equal ( '999999', "1.0000e+6")
	equal (  '99999', "9.9999e+4")
	equal (   '9999', "9.9990e+3")
	equal (    '999', "9.9900e+2")
	equal (     '99', "9.9000e+1")
	equal (      '9', "9.0000e+0")

	equal (      '1', "1.0000e+0")
	
	equal (    '0.1', "1.0000e-1")
	equal (   '0.01', "1.0000e-2")
	equal (  '0.001', "1.0000e-3")
	
	equal (      '0', "0.0000e+0")

	equal ( '-0.001', "-1.0000e-3")
	equal (  '-0.01', "-1.0000e-2")
	equal (   '-0.1', "-1.0000e-1")	
	equal (   '-0.9', "-9.0000e-1")
	
	
	equal (     '-9', "-9.0000e+0")
	equal (    '-99', "-9.9000e+1")
	equal (   '-999', "-9.9900e+2")
	
checks = {
	"status 1": status_1
}