'''
dev.py

This file holds constants and functions meant for
development.
'''

from typing import List
import builder.proc_constraints as proc
import builder.io_file as io_file
import builder.models as models




def dummyProjectState() -> models.ProjectState:
	varnamesRaw = io_file.readVarnamesRaw(
		'../sample-data/obj_minimodel_smol.csv', 
		)

	varData = proc.buildVarDataObject(
		varnamesRaw,
		'_', 
		['for_type', 'year', 'mng']
		)

	# TODO: Actually have some constraints here for testing
	constrGroupList: List[models.ConstraintGroup] = []

	setupList = [
		models.SetupConstraintGroup.createEmptySetup(varData),
		# models.SetupConstraintGroup.createFullSetup(varData)
	] * 20

	return models.ProjectState(
		varData = varData,
		setupList=setupList
		# constraintList = constrGroupList
	)



