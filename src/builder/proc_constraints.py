'''
Constraint Processor

This file does processing with constraints
 - Generating constraint classes from user input
 - Converting some formats between each other
 - Modifying projectstate
 - Reading projectstate from files

Michael Gorbunov
NJDEP / NJFS
Started 05/21/2022
'''

from copy import deepcopy
from typing import List, Dict, Union
import itertools

import builder.models as models
import builder.io_cmd as io_cmd
import builder.io_file as io_file
import builder.proc_linting as lint


# TODO:
# [~] Come up with better names (groups, vars, varGroupList, etc is _really_ confusing)
# [x] Be more strict with delimiting
#    - Only allow for one character in the delimiting ?
# [x] Have dataclass for constraint classes
#    - There should be a sense of an abstract constraint class (group members)
#      and a concrete constraint class (which can be exactly compiled into constraints)
# [ ] Instead of returning lists of copmiled constraints, return an iterator or generator function
# [ ] Have a way to be Exclusive or Inclusive with categories ??
#    - We may want a constriant that for example applies to all but 2 tree species, and this would allow
#      for generalizing the scripts for other obj inputs (other states ?)
# [ ] Add type checks for important processing functions

def makeTagGroupMembersList (varnamesRaw: List[str], delim: str) -> List[List[str]]:
	'''
		Takes a list of variables in the form

		[	"167S_2021_NM",
		 	"167S_2025_NM",
		 	"167N_2025_NM",
		 	"167N_2030_SBP"	]

		and returns lists of tags in individual groups
		in the order they appear within the variables.

		[	[167S, 167N],      
			[2021, 2025, 2030],
			[NM, SBP]	] 
	'''
	tagGroupMembers = []
	for _ in range(len(varnamesRaw[0].split(delim))):
		tagGroupMembers.append(set())
	
	for varName in varnamesRaw:
		varTags = varName.split(delim)
		for ind, groupID in enumerate(varTags):
			tagGroupMembers[ind].add(groupID)

	for ind, tags in enumerate(tagGroupMembers):
		tagGroupMembers[ind] = list(tags)
		tagGroupMembers[ind].sort()

	return tagGroupMembers


def buildVarDataObject (varnamesRaw: List[str], delim: str, tagGroupNames: List[str]) -> models.VarsData:
	'''
		Builds a varData object with the given user input.

		DOES NOT LINT. Make sure to call the linting functions before passing into this.
		With poor data, this will throw an error (or worse, fail silently)
	'''
	sortedVarsRaw = deepcopy(varnamesRaw)
	sortedVarsRaw.sort()
	tagGroupMembersList = makeTagGroupMembersList(varnamesRaw, delim)

	tagGroupsDict = {}
	for ind, name in enumerate(tagGroupNames):
		tagGroupsDict[name] = tagGroupMembersList[ind]

	return models.VarsData(
		delim = delim,
		tag_order = tagGroupNames,
		all_vars = [x.split(delim) for x in sortedVarsRaw],
		tag_members = tagGroupsDict
	)


def buildConstraintGroup (groupSetup: models.SetupConstraintGroup, varData: models.VarsData) -> models.ConstraintGroup:
	'''
	Generates a constraint group, which holds the actual equations, from the 
	specification of a SetupConstraintGroup.

	Takes a setup object (SetupConstraintGroup), and a varData object.
	'''
	# I apologize to future me if I ever have to refactor this, this is a tad convoluted ...
	delim: str = varData.delim

	# Generate all applicable variables
	allLeftVars: List[List[str]] = []
	allRightVars: List[List[str]] = []

	leftSelAsList = [groupSetup.selLeftTags[k] for k in varData.tag_order]
	for tags in itertools.product(*leftSelAsList):
		allLeftVars.append(list(tags))

	rightSelAsList = [groupSetup.selRightTags[k] for k in varData.tag_order]
	for tags in itertools.product(*rightSelAsList):
		allRightVars.append(list(tags))

	# Now split them into seperate equations
	allSelectedVars: List[List[str]] = deepcopy(leftSelAsList)
	for ind, _ in enumerate(varData.tag_order):
		for mem in rightSelAsList[ind]:
			if mem not in allSelectedVars[ind]:
				allSelectedVars[ind].append(mem)
	
	allSelectedSplits: List[List[str]] = []
	for ind, tagGroup in enumerate(varData.tag_order):
		if tagGroup in groupSetup.splitBy:
			allSelectedSplits.append(allSelectedVars[ind])
		else:
			allSelectedSplits.append([None])

	actuallyAllLeftVars: List[List[str]] = []
	actuallyAllRightVars: List[List[str]] = []
	for tags in itertools.product(*leftSelAsList):
		if list(tags) in varData.all_vars:
			actuallyAllLeftVars.append(list(tags))
	for tags in itertools.product(*rightSelAsList):
		if list(tags) in varData.all_vars:
			actuallyAllRightVars.append(list(tags))

	eqList: List[models.Equation] = []

	for split in itertools.product(*allSelectedSplits):
		leftsideVars = []
		rightsideVars = []

		for x in actuallyAllLeftVars:
			if all([split[ind] == None or split[ind] == y 
				for ind, y in enumerate(x)]):
					leftsideVars.append(x)

		for x in actuallyAllRightVars:
			if all([split[ind] == None or split[ind] == y
				for ind, y in enumerate(x)]):
					rightsideVars.append(x)

		# Check if it's an empty constraint
		if len(leftsideVars) == 0 and len(rightsideVars) == 0:
			continue
		
		# Now we can construct the equation
		suffix = None
		if all([x == [None] for x in allSelectedSplits]):
			suffix = ''
		else:
			suffix = delim.join(filter(lambda mem: mem != None, split))

		eqList.append(
			models.Equation(
				namePrefix=groupSetup.namePrefix,
				nameSuffix=suffix,
				constant=groupSetup.defConstant,
				comparison=groupSetup.defComp,
				leftVars=leftsideVars,
				leftCoefs=[groupSetup.defLeftCoef] * len(leftsideVars),
				rightVars=rightsideVars,
				rightCoefs=[groupSetup.defRightCoef] * len(rightsideVars)
			)
		)

	return models.ConstraintGroup(
		groupName=groupSetup.namePrefix,
		equations=eqList,
		SPLIT_BY=groupSetup.splitBy,
		DEFAULT_COMPARE=groupSetup.defComp,
		DEFAULT_LEFT_COEF=groupSetup.defLeftCoef,
		DEFAULT_RIGHT_COEF=groupSetup.defRightCoef
	)


def getNumConstraints (setup: models.SetupConstraintGroup, varData: models.VarsData) -> int:
	'''
	Returns how many constraints exist in the setup object.

	This is done by actually building the constriant group object.
	'''
	return len(buildConstraintGroup(setup, varData).equations)


def changeVarsData (newVarData: models.VarsData, projectstate: models.ProjectState) -> models.ProjectState:
	'''
	Given a new varData (eg: new objective file), will update projectState and
	all of its constraintGroups so they use new variables only.
	'''
	oldVarData = projectstate.varData
	newstate: models.ProjectState = models.ProjectState(
		varData=newVarData,
		setupList=[]
	)

	newGroups = list(set(newVarData.tag_order) - set(oldVarData.tag_order))
	sameGroups = list(set(newVarData.tag_order).intersection(set(oldVarData.tag_order)))


	for const in projectstate.setupList:
		newsplits = []
		for x in const.splitBy:
			if x in newVarData.tag_order:
				newsplits.append(x)

		# Transfer over the tags that stayed the same
		newLeftTags = {}
		newRightTags = {}

		for tagGroup in sameGroups:
			removedTags = list(
				set(oldVarData.tag_members[tagGroup]) - 
				set(newVarData.tag_members[tagGroup])
				)

			# print(f"Const: {const.namePrefix}")
			# print(f"Removed: {list(removedTags)}")
			# print()

			transferedLeft = []
			for x in const.selLeftTags[tagGroup]:
				if not x in removedTags:
					transferedLeft.append(x)
			newLeftTags[tagGroup] = transferedLeft

			transferRight = []
			for x in const.selRightTags[tagGroup]:
				if not x in removedTags:
					transferRight.append(x)
			newRightTags[tagGroup] = transferRight
		
		for tagGroup in newGroups:
			newLeftTags[tagGroup] = []
			newRightTags[tagGroup] = []

		# Add to list
		newconst = models.SetupConstraintGroup(
			namePrefix=const.namePrefix,
			splitBy=newsplits,
			defComp=const.defComp,
			defLeftCoef=const.defLeftCoef,
			defRightCoef=const.defRightCoef,
			defConstant=const.defConstant,
			selLeftTags=newLeftTags,
			selRightTags=newRightTags
		)
		newstate.setupList.append(newconst)

	return newstate





#
# Working with the model
#


_model_versions = [
	models.ProjectState,
	models.ProjectState_V0_0
]

def readProjectStateFile (filepath: str) -> Union[models.ProjectState, str]:
	'''
	Attempts to read the project file at the filepath.

	If reading an older project file, will convert up
	to a more recent version.

	Returns None and an error message if unsuccesful.
	'''
	fileData = None
	try:
		with open(filepath, 'r') as file:
			fileData = file.read()
	except:
		pass

	if fileData == None:
		return None, "Unable to read file"
	
	# See if the data is in fact a model file
	model = None
	for m in _model_versions:
		try:
			model = models.fromOutputStr(fileData, m)
		except:
			continue
	
	if model == None:
		return None, "Not a valid project file, unable to parse"
	
	# Cast the model up
	while not isinstance(model, models.ProjectState):
		_prevModel = model
		model = model.convertUp()

		if _prevModel == model:
			return None, "Conversion code is messed up"

	# Fix Up
	model = lint.fixupIllegalProjectState(model)

	return model, None
	






if __name__ == '__main__':
	import builder.devtesting as devtesting
	import json
	import cattrs
	from pprint import pprint

	# Input
	objCSVPath = '/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM-Builder/sample-data/obj_minimodel_diff.csv'

	varnamesRaw = io_file.readVarnamesRaw(objCSVPath)
	# delim = input(f"Sample Var '{varnamesRaw[0]}' | Delimiter: ")
	delim = '_'
	errMsg = lint.lintAllVarNamesRaw(varnamesRaw, delim)
	if errMsg:
		io_cmd.errorAndExit(errMsg)

	tagMems = makeTagGroupMembersList(varnamesRaw, delim)
	# tagNames = io_cmd.getTagGroupNames(tagMems)
	tagNames = ['for_type', 'year', 'mng']
	errMsg = lint.lintAllTagGroupNames(tagNames)
	if errMsg:
		io_cmd.errorAndExit(errMsg)

	# Processing
	varInfo = buildVarDataObject(varnamesRaw, delim, tagNames)


	# Constraint Testing
	setupConstr = models.SetupConstraintGroup.createEmptySetup(varInfo)
	setupConstr.splitBy = ['for_type']

	selectedLeft = {
		'for_type': ['167N', '167S'],
		'year': ['2030', '2050'],
		'mng': ['STQO', 'PLSQ']
	}

	selectedRight = {
		'for_type': ['167N', '505'],
		'year': ['2021', '2025'],
		'mng': ['IFM', 'THNB']
	}

	setupConstr.selLeftTags = selectedLeft
	setupConstr.selRightTags = selectedRight

	print(f"Setup:")
	print(models.toOutputStr(setupConstr, models.SetupConstraintGroup, pretty=True))

	# Processing
	actualConstraint = buildConstraintGroup(setupConstr, varInfo)

	print("\n\n")
	for eq in actualConstraint.equations:
		print("\n ======")
		print(eq)
	print(f"Constr: \n{actualConstraint}\n")





'''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠟⠉⠉⠉⠉⠉⠉⠉⠙⠻⢶⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣠⣶⠛⠛⠛⠛⠛⠛⠳⣦⡀⠀⠘⣿⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠁⠀⢹⣿⣦⣀⣀⣀⣀⣀⣠⣼⡇⠀⠀⠸⣷⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡏⠀⠀⠀⠉⠛⠿⠿⠿⠿⠛⠋⠁⠀⠀⠀⠀⣿⡄⣠
⠀⠀⢀⣀⣀⣀⠀⠀⢠⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡇⠀
⠿⠿⠟⠛⠛⠉⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⠀
⠀⠀⠀⠀⠀⠀⠀⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠀⠀⠀⠀⠀⠀⠀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠀⠀⠀⠀⠀⠀⢰⣿⠀⠀⠀⠀⣠⡶⠶⠿⠿⠿⠿⢷⣦⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠀⠀⣀⣀⣀⠀⣸⡇⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⣿⠀
⣠⡿⠛⠛⠛⠛⠻⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⣿⠀
⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⡟⠀⠀⢀⣤⣤⣴⣿⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠈⠙⢷⣶⣦⣤⣤⣤⣴⣶⣾⠿⠛⠁⢀⣶⡟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡟⠀
⢷⣶⣤⣀⠉⠉⠉⠉⠉⠄⠀⠀⠀⠀⠈⣿⣆⡀⠀⠀⠀⠀⠀⠀⢀⣠⣴⡾⠃⠀
⠀⠈⠉⠛⠿⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠈⠛⠻⢿⣿⣾⣿⡿⠿⠟⠋⠁⠀⠀⠀


			 Why so Sus ?

'''
