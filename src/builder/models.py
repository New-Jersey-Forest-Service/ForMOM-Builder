'''
Variable Names

This file has an attrs class for storing variable names
and groups.

Michael Gorbunov
NJDEP
'''

import json
import attrs
import cattrs
from enum import Enum, unique, auto
from typing import Any, List, Dict, Type, Union
from copy import deepcopy







#
# Program State Dataclasses

@unique
class ComparisonSign(Enum):
	GE = '>='
	LE = '<='
	EQ = '=='

	def toSymbols (self) -> str:
		return self._value_
	
	def exportName (self) -> str:
		return _toExportName[self]

	@staticmethod
	def fromSybols (symbols: str):
		stripped = symbols.strip()

		if not stripped in _compSignMap.keys():
			return None
		return _compSignMap[stripped]

_toExportName = {
	ComparisonSign.GE: 'ge',
	ComparisonSign.LE: 'le',
	ComparisonSign.EQ: 'eq'
}

_compSignMap = {}
for cs in ComparisonSign:
	_compSignMap[cs._value_] = cs




@attrs.frozen
class VarsData:
	'''
	Stores all data needed to reconstruct and work with the variables.

	delim: The seperating character
	tag_order: List of the tags, in order that they appear
	all_vars: List of variables, where variables are stored as lists of their tags
	tag_members: Dictionary between a tag group (from tag_order) and which tags it has

	== Example
	variables = ['167N_PLSQ_2021', '167N_THNB_2021', '167N_PLSQ_2025']

	# Basically from user Input
	delim = '_' 
	tag_order = ['for_type', 'mng', 'year'] (user input)

	# Generated
	all_vars = [ ['167N', 'PLSQ', '2021'], ['167N', 'THNB', '2021'], ['167N', 'PLSQ', '2025']]
	tag_members = {
		'for_type': ['167N'],
		'mng': ['PLSQ', 'THNB'],
		'year': ['2021', '2025']
	}
	'''
	delim: str
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_members: Dict[str, List[str]]
















@attrs.define
class Equation:
	namePrefix: str
	nameSuffix: str
	constant: float
	comparison: ComparisonSign

	leftVars: List[List[str]]
	leftCoefs: List[float]
	rightVars: List[List[str]]
	rightCoefs: List[float]

	# def getName(self):
	# 	return self.namePrefix + self.nameSuffix


@attrs.define
class ConstraintGroup:
	'''
	Stores actual equations, and is generated from a SetupConstraintGroup.
	'''
	groupName: str
	equations: List[Equation]

	# The plan was for there to eventually be a fine-tuning screen
	# where you could modify individual equations, coefficients, etc.
	# Otherwise, these values serve no purpose
	SPLIT_BY: List[str]
	DEFAULT_COMPARE: ComparisonSign
	DEFAULT_LEFT_COEF: float
	DEFAULT_RIGHT_COEF: float


@attrs.define
class SetupConstraintGroup:
	'''
	Contains the information needed to generate a list of equations, aka constraints.

	namePrefix: The starting name of a constraint
	splitBy: Which tags to split by. Eg: ['for_type', 'mng'] when all tags are ['for_type', 'mng', 'year']
	defComp: Default comparison
	defLeftCoef: Default coefficient for variables on the left
	defRightCoef: Default coefficient for right variabels
	defConstant: Default value to be added on the right

	selLeftTags: Which tags are selected for equations on the left
	selRightTags: Which tags are selected for equations on the right
	'''
	namePrefix: str
	splitBy: List[str]
	defComp: ComparisonSign
	defLeftCoef: float
	defRightCoef: float
	defConstant: float

	selLeftTags: Dict[str, List[str]]
	selRightTags: Dict[str, List[str]]

	@staticmethod
	def createEmptySetup(varData: VarsData):
		selectedTags = {}
		for tag in varData.tag_order:
			selectedTags[tag] = []
		
		return SetupConstraintGroup(
			namePrefix="unnamed",
			splitBy=[],
			defComp=ComparisonSign.EQ,
			defLeftCoef=1.0,
			defRightCoef=1.0,
			defConstant=0,
			selLeftTags=selectedTags,
			selRightTags=deepcopy(selectedTags)
		)
	
	@staticmethod
	def createFullSetup(varData: VarsData):
		'''
		Creates a setupConstraintGroup with all setting set to non-zero values,
		and all tags selected. Useful for testing.
		'''
		selectedTags = {}
		for tag in varData.tag_order:
			selectedTags[tag] = deepcopy(varData.tag_members[tag])
		
		return SetupConstraintGroup(
			namePrefix="unnamed_full",
			splitBy=deepcopy(varData.tag_order),
			defComp=ComparisonSign.EQ,
			defLeftCoef=2.0,
			defRightCoef=1.0,
			defConstant=10,
			selLeftTags=selectedTags,
			selRightTags=deepcopy(selectedTags)
		)












#
# Project State Classes
#
# These classes get exported (basically as json) into .cproj files.
# They store _everything_ for a project.

@attrs.define
class ProjectState:
	varData: VarsData
	# constraintList: List[ConstraintGroup]
	setupList: List[SetupConstraintGroup]

	# The actual value of the version doesn't matter
	# what matters is each new version has a different
	# variable name
	VERSION01: str = None

	@staticmethod
	def createEmptyProjectState ():
		return ProjectState(
			None, None
		)


@attrs.define
class ProjectState_V0_0:
	'''
	This class is the original project state class. 
	If a project file is read into this format, convertUp() is called
	to convert it to the newest version.

	You will notice, there is no difference between these two project state versions.
	'''
	varData: VarsData
	setupList: List[SetupConstraintGroup]

	# This state is before versioning was added, hence no version number
	
	def convertUp(self) -> ProjectState:
		'''
			Converts this object into a more recent project state
		'''
		new_self = deepcopy(self)

		return ProjectState(
			varData=new_self.varData,
			setupList=new_self.setupList
		)



	




def toOutputStr (obj: Any, type: Type, pretty=False) -> str:
	'''
	Turns the passed python object into a string. Useful for human-readable
	serialization.

	Pretty = True will format the json with indents, and across multiple lines.
	'''
	if not isinstance(obj, type):
		objType = type(obj)
		raise TypeError(f"Expected {type} got {objType} ")
	
	if not pretty:
		return json.dumps(cattrs.unstructure(obj))
	else:
		return json.dumps(cattrs.unstructure(obj), indent=2)


# TODO: How do I type annotate this ??
def fromOutputStr (strObj: str, type: Type):
	try:
		return cattrs.structure_attrs_fromdict(json.loads(strObj), type)
	except Exception as e:
		# print("[[ XX ERROR ]] Unable to read file. It may be corrupt or comes from an older version of the program")
		# print()
		raise e







