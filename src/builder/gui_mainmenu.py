'''
Main Screen

This gives the user the option to load a project or start fresh.
'''

import tkinter as tk
import tkinter.messagebox as tkmsg
from tkinter import ttk

import builder.gui_newproject as gui_newproject
import builder.gui_projectoverview as gui_projectoverview
import builder.io_file as io_file
import builder.models as models
import builder.proc_constraints as proc
from builder.gui_consts import *

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None




#
# Update Calls
#

def updateNewProj():
	global _passedProjectState

	_passedProjectState = models.ProjectState.createEmptyProjectState()

	transitionToObjImport()


def updateLoadProj():
	global _passedProjectState

	projFilepath: str = io_file.getOpenFilepath(PROJ_FILES)
	newProjState, err = proc.readProjectStateFile(projFilepath)

	if err != None:
		tkmsg.showerror(
			title="Load File Error", 
			message=f"Unable to open project: {err}")
		return
	
	_passedProjectState = newProjState
	
	transitionToOverview()






#
# Transition Calls
#

def transitionToObjImport() -> None:
	global _passedProjectState, _passedRoot

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_newproject.buildGUI_ObjImport(_passedRoot, _passedProjectState)


def transitionToOverview() -> None:
	global _passedProjectState, _passedRoot

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_projectoverview.buildGUI_ProjectOverview(_passedRoot, _passedProjectState)




#
# Main GUI Construction
#

def buildGUI_OpeningScreen(root: tk.Tk, projectState: models.ProjectState):
	global _passedProjectState, _passedRoot

	_passedProjectState = projectState
	_passedRoot = root

	root.title("NJDEP Constraint Builder")

	root.columnconfigure(0, weight=1)
	root.rowconfigure(1, weight=1)

	lblHeader = tk.Label(root, text="NJDEP Constraint Builder", font=("Arial", 16), anchor="center")
	lblHeader.grid(row=0, column=0, sticky="ew", padx=20, pady=10)


	frmOptions = tk.Frame(root)
	frmOptions.grid(row=1, column=0, sticky="")

	btnNewProj = tk.Button(frmOptions, text="New Constraint Project", command=updateNewProj)
	btnNewProj.grid(row=0, column=0, sticky="ew", pady=5)

	btnLoadProj = tk.Button(frmOptions, text="Open Project", command=updateLoadProj)
	btnLoadProj.grid(row=1, column=0, sticky="ew", pady=5)


	lblSubInfo = tk.Label(root, text="ForMOM Project\nDev: Michael Gorbunov, Bill Zipse\nTest & QA: Courtney Willits, Lauren Gazerwitz, \nBen Pisano, Justin Gillmero", anchor="e", justify="right")
	lblSubInfo.grid(row=2, column=0, sticky="se", padx=20, pady=(0, 20))






if __name__ == '__main__':
	projectState = models.ProjectState.createEmptyProjectState()

	root = tk.Tk()
	buildGUI_OpeningScreen(root, projectState)
	root.mainloop()


