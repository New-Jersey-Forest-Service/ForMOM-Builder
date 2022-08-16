'''
Processor for (string) Rendering

This file contains methods for string manipulation and converting data to strings.
'''

from typing import List

import builder.models as models




def trimEllipsisLeft (baseStr: str, maxLen: int) -> str:
	'''
	Converts "Fsdfsadff1111" => "... sadff1111"
	'''
	if len(baseStr) <= maxLen:
		return baseStr
	
	ELLIPSIS = "... "
	return ELLIPSIS + baseStr[len(ELLIPSIS)-maxLen:]


def trimEllipsisRight (baseStr: str, maxLen: int) -> str:
	'''
	Converts "Fsdfsadff1111" => "Fsdfsad ..."
	'''
	if len(baseStr) <= maxLen:
		return baseStr
	
	ELLIPSIS = " ..."
	return baseStr[:maxLen - len(ELLIPSIS)] + ELLIPSIS


def renderSingleEq (eq: models.Equation, delim: str, charwidth:int=-1) -> str:
	leftVarsStr = _renderVarsString(eq.leftVars, eq.leftCoefs, delim)
	rightVarStr = _renderVarsString(eq.rightVars, eq.rightCoefs, delim)

	finalStr = eq.namePrefix
	if eq.nameSuffix != "":
		finalStr += delim + eq.nameSuffix
	finalStr += "\n"
	finalStr += leftVarsStr + " " + eq.comparison.toSymbols() + " " + rightVarStr
	finalStr += " + " + str(eq.constant)
	finalStr += "\n"

	return finalStr



def _renderVarsString (varTags: List[List[str]], varCoefs: List[float], delim: str) -> str:
	varStrs: List[str] = [delim.join(tags) for tags in varTags]
	coefVarStrs: List[str] = []

	for ind, varStr in enumerate(varStrs):
		coef = varCoefs[ind]

		coefStr = ''
		if coef == 1:
			pass
		elif coef == int(coef):
			coefStr = str(int(coef)) + "*"
		else:
			coefStr = str(coef) + "*"
		
		coefVarStrs.append(coefStr + varStr)
	
	return " + ".join(coefVarStrs)
		
		
def renderConstraintGroup (group: models.ConstraintGroup, delim: str, charwidth:int=-1) -> str:
	NUM_EQS = 5
	eqs = group.equations[:NUM_EQS]

	# print(f"In render method. # Eqs: {len(eqs)}, Eqs: {eqs}")
	# print(f"In render method. # Eqs: {len(eqs)}")

	if len(eqs) == 0:
		return "No Constraints Exist"

	finalStr = ""
	for eq in eqs:
		finalStr += renderSingleEq(eq, delim, charwidth)
		finalStr += "\n"
	
	return finalStr






if __name__ == '__main__':
	print(trimEllipsisRight("1234567890", maxLen=7))
	print(trimEllipsisLeft("1234567890", maxLen=7))





