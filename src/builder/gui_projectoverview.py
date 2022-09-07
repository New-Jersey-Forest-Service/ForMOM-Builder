'''
Constraint Builder Constraints Overview Screen
'''

import copy
import csv
import tkinter as tk
from tkinter import ttk
from typing import List

import builder.proc_constraints as proc
import builder.proc_render as render
import builder.gui_variablefiltering as gui_variablefiltering
import builder.gui_newcsv as gui_newcsv
import builder.models as models
import builder.devtesting as devtesting
import builder.io_file as io_file
from builder.gui_consts import *

# Exposed GUI Elements
_frmConstrsDisplay: tk.Frame = None
_lblSummary: tk.Label = None


# State Variables
_constrGroupList: List[models.SetupConstraintGroup] = None

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None

# Calculated from _constrGroupList
_constrPerGroup: List[int] = None
_varsConstrainted: List[List[str]] = None

# This will be useful for scrolling
# https://stackoverflow.com/questions/68056757/how-to-scroll-through-tkinter-widgets-that-were-defined-inside-of-a-function








#
# Update Calls
#

def updateDeleteConstrGroup (constrInd: int) -> None:
	global _constrGroupList
	print(f"Deleteting {_constrGroupList[constrInd].namePrefix}")

	_constrGroupList.pop(constrInd)

	redrawConstrUpdate(_constrGroupList)


def updateNewConstrGroup () -> None:
	global _constrGroupList
	print(f"Adding a new constraint")

	_constrGroupList.append(models.SetupConstraintGroup.createEmptySetup(_passedProjectState.varData))

	redrawConstrUpdate(_constrGroupList)


# TODO: Move so much of this into fileio
def updateSaveProject () -> None:
	print("Saving project file")

	outputFilepathStr = io_file.getSaveAsFilepath(PROJ_FILES)
	if outputFilepathStr == None:
		return

	projectDataStr = models.toOutputStr(_passedProjectState, models.ProjectState)
	with open(outputFilepathStr, 'w') as outFile:
		outFile.write(projectDataStr)


def updateExportCSV () -> None:
	print("Exporting to csv")

	outputFilepathStr = io_file.getSaveAsFilepath(CSV_FILES)
	if outputFilepathStr == None:
		return
	io_file.writeToCSV(outputFilepathStr, _passedProjectState)
	
	print(":D File Written")








#
# Transition Calls
#

def transitionToEditing (constrInd: int) -> None:
	global _constrGroupList, _passedProjectState, _passedRoot
	print(f"Editing {_constrGroupList[constrInd].namePrefix}")

	_passedProjectState.setupList = _constrGroupList

	for child in _passedRoot.winfo_children():
		child.destroy()

	gui_variablefiltering.buildGUI_VariableFiltering(_passedRoot, _passedProjectState, constrInd)


def transitionToObjReplace () -> None:
	global _passedProjectState, _passedRoot
	print(f"Going to objective file replacement screen")

	_passedProjectState.setupList = _constrGroupList

	for child in _passedRoot.winfo_children():
		child.destroy()
	
	newGui = gui_newcsv.GUINewCSV(_passedRoot, _passedProjectState)
	













#
# Redraw Calls
#

def redrawConstrUpdate (constrGroupList: List[models.SetupConstraintGroup]) -> None:
	global _constrPerGroup, _varsConstrainted

	print("Constraint update")

	# Generate global data
	_constrPerGroup = []
	_varsConstrainted = []

	for cGroup in constrGroupList:
		fullConstraint = proc.buildConstraintGroup(cGroup, _passedProjectState.varData)

		_constrPerGroup.append(len(fullConstraint.equations))

		for eq in fullConstraint.equations:
			for var in eq.leftVars + eq.rightVars:
				if var not in _varsConstrainted:
					_varsConstrainted.append(var)

	redrawConstrListFrame(constrGroupList)
	redrawSummaryStats()


def redrawConstrListFrame (constrGroupList: List[models.SetupConstraintGroup]) -> None:
	global _frmConstrsDisplay

	for child in _frmConstrsDisplay.winfo_children():
		child.destroy()

	CONSTRS_PER_ROW = 5
	ALTERNATING_COLORS = ['#BBBBBB', '#EAEAEA']
	_frmConstrsDisplay.columnconfigure([x for x in range(CONSTRS_PER_ROW)], weight=1)

	# Render everything
	for ind, constrGroup in enumerate(constrGroupList):
		_row = ind // CONSTRS_PER_ROW
		_col = ind % CONSTRS_PER_ROW

		frmConstr = tk.Frame(_frmConstrsDisplay, relief=tk.RIDGE, bd=2)
		frmConstr.grid(
			row=_row,
			column=_col,
			sticky="ew", 
			pady=(0, 10),
			padx=5
			)
		frmConstr.columnconfigure(1, weight=1)

		if _row % 2 == 1:
			frmConstr.configure(bg=ALTERNATING_COLORS[0])
		else:
			frmConstr.configure(bg=ALTERNATING_COLORS[1])
		
		name = render.trimEllipsisRight(constrGroup.namePrefix, WIDTH_BIG)
		lblName = tk.Label(frmConstr, text=name)
		lblName.grid(row=0, column=0, sticky="w", padx=10, pady=5)

		frmNum = tk.Frame(frmConstr, bd=1)
		frmNum.grid(row=0, column=1, sticky="e", padx=5, pady=5)

		numConstrs = _constrPerGroup[ind]
		lblNum = tk.Label(frmNum, text=numConstrs)
		lblNum.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

		if numConstrs == 0:
			frmNum.configure(bg='red')
			lblNum.configure(bg='#E09996')

		btnDelete = tk.Button(frmConstr, text="Delete", command=lambda ind=ind: updateDeleteConstrGroup(ind))
		btnDelete.grid(row=0, column=2, sticky="e", padx=5, pady=5)

		btnEdit = tk.Button(frmConstr, text="Edit >", command=lambda ind=ind: transitionToEditing(ind))
		btnEdit.grid(row=0, column=3, sticky="e", padx=5, pady=5)


def redrawSummaryStats ():
	global _lblSummary
	
	allVars = _passedProjectState.varData.all_vars

	allConNames = [x.namePrefix for x in _passedProjectState.setupList]
	duplicateConCames = [x for x in allConNames if allConNames.count(x) > 1]
	duplicateConCames = list(set(duplicateConCames))

	unconVars = set(map(lambda x: "_".join(x), allVars)) - set(map(lambda x: "_".join(x), _varsConstrainted))
	unconVars = list(unconVars)

	# Build the summary string
	summaryStr = ""

	totConstrs = sum(_constrPerGroup)
	totUnConVars = len(unconVars)
	totVarsUsed = len(allVars) - totUnConVars

	summaryStr += f'Constraints: {totConstrs}\n'
	summaryStr += f'Variables Used: {totVarsUsed}\n'
	summaryStr += f'Variables Not Used: {totUnConVars}'

	# display duplicate named constraint groups
	if len(duplicateConCames) != 0:
		summaryStr += "\n\n"
		summaryStr += f"Duplicate Constriant Names:\n"
		summaryStr += ", ".join(duplicateConCames)

	# display unconstrained variables
	if len(unconVars) != 0:
		summaryStr += "\n\n"

		NUM_UNCON_TO_SHOW = 10
		if len(unconVars) > NUM_UNCON_TO_SHOW:
			summaryStr += f'First {NUM_UNCON_TO_SHOW} '
			unconVars = unconVars[:NUM_UNCON_TO_SHOW]
		summaryStr += 'unconstrained variables:\n'
		summaryStr += ", ".join(unconVars)

	# Update
	_lblSummary.configure(text=summaryStr)












#
# Main GUI Construction
#

def buildGUI_ProjectOverview(root: tk.Tk, projectState: models.ProjectState) -> None:
	global _constrGroupList, _passedRoot, _passedProjectState

	_passedProjectState = projectState
	_passedRoot = root
	_constrGroupList = projectState.setupList

	root.title("Constraint Builder - Project Overview")
	root.rowconfigure(1, weight=1)
	root.columnconfigure([0, 1], weight=1)

	# Header text
	lblHeader = tk.Label(root, text="Project Overview")
	lblHeader.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0))

	# Constraint Groups Display
	frmConstrsDisplay = buildConstraintGroupListFrame(root)
	frmConstrsDisplay.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")

	# New Constraint Group
	frmNewConstrBtn = buildConstraintButtonFrame(root)
	frmNewConstrBtn.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")

	# Summary Info Frame
	frmSummary = buildSummaryInfoFrame(root)
	frmSummary.grid(row=3, column=0, padx=10, pady=10)

	# Exporting Buttons
	frmExport = buildExportButtonsFrame(root)
	frmExport.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="es")


	print("GUI Build, now redrawing some othe info")
	redrawConstrUpdate(_constrGroupList)
	

def buildConstraintGroupListFrame(root: tk.Tk) -> tk.Frame:
	global _frmConstrsDisplay

	_frmConstrsDisplay = tk.Frame(root)
	_frmConstrsDisplay.columnconfigure(0, weight=1)

	return _frmConstrsDisplay


def buildConstraintButtonFrame(root: tk.Tk) -> tk.Frame:
	frmNewConstrBtn = tk.Frame(root)
	frmNewConstrBtn.columnconfigure(0, weight=1)

	btnNew = tk.Button(frmNewConstrBtn, text="New Constraint Group", anchor="center", command=updateNewConstrGroup)
	btnNew.grid(row=0, column=0)

	return frmNewConstrBtn


def buildExportButtonsFrame(root: tk.Tk) -> tk.Frame:
	frmExport = tk.Frame(root)
	frmExport.columnconfigure([x for x in range(1000)], weight=1)

	btnChangeCsv = ttk.Button(frmExport, text="Change Objective .csv", command=transitionToObjReplace)
	btnChangeCsv.grid(row=0, column=0, sticky="e", padx=10)

	btnSaveProj = tk.Button(frmExport, text="Save Project", command=updateSaveProject)
	btnSaveProj.grid(row=0, column=1, sticky="e")

	btnExportProj = tk.Button(frmExport, text="Export to .csv", command=updateExportCSV)
	btnExportProj.grid(row=0, column=2, sticky="e", padx=10, pady=10)

	return frmExport


def buildSummaryInfoFrame(root: tk.Tk) -> tk.Frame:
	global _lblSummary

	frmSummary = tk.Frame(root, padx=5, pady=10, bd=1, relief=tk.SUNKEN, height=WIDTH_SML)
	frmSummary.columnconfigure(0, weight=1)

	_lblSummary = tk.Label(frmSummary, wrap=300, width=WIDTH_BIG, justify="left")
	_lblSummary.configure(text = "Hi this is a summary and so has a lot of text please be patient")
	_lblSummary.grid(row=0, column=0, sticky="nsew")

	return frmSummary




if __name__ == '__main__':
	projState = devtesting.dummyProjectState()

	root = tk.Tk()
	buildGUI_ProjectOverview(root, projState)
	root.mainloop()




'''
	Treet others how you want to be treeted

			  v .   ._, |_  .,
		   `-._\/  .  \ /	|/_
			   \\  _\, y | \//
		 _\_.___\\, \\/ -.\||
		   `7-,--.`._||  / / ,
		   /'	 `-. `./ / |/_.'
					 |	|//
					 |_	/
					 |-   |
					 |   =|
					 |	|
--------------------/ ,  . \--------._
  jg
'''


