'''
New Constraint Builder Constraints Overview Screen
'''



'''





This file is not used. You may ignore it.
























'''



import copy
import csv
from pprint import pprint
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
from builder.scrolllableframe import ScrollableFrame
from builder.gui_consts import *




class ProjectoverviewNewApp:

    # State Variables
    _constrGroupList: List[models.SetupConstraintGroup] = None

    _passedProjectState: models.ProjectState = None
    _passedRoot: tk.Tk = None

    # Calculated from _constrGroupList
    _constrPerGroup: List[int] = None
    _varsConstrainted: List[List[str]] = None



    def __init__(self, root:tk.Tk, projState: models.ProjectState):
        self._passedProjectState = projState

        self._build_ui(root)
        self._redrawEverything()


    def _build_ui(self, master):
        # build ui
        self.top = ttk.Frame(master)
        self.frm_title = ttk.Frame(self.top)
        self.lbl_title = ttk.Label(self.frm_title)
        self.lbl_title.configure(
            anchor="center", justify="center", text="Project Overview"
        )
        self.lbl_title.grid(column=0, padx=5, pady=5, row=0, sticky="ew")
        self.frm_title.configure(height=200, width=200)
        self.frm_title.grid(column=0, columnspan=2, row=0, sticky="ew")
        self.frm_title.columnconfigure(0, weight=1)
        self.frm_constraints = ttk.Frame(self.top)
        self.frm_constraint_editing = ttk.Frame(self.frm_constraints)
        self.btn_edit = ttk.Button(self.frm_constraint_editing)
        self.btn_edit.configure(text="Edit >")
        self.btn_edit.grid(column=1, padx=5, pady=5, row=0, sticky="e")
        self.btn_edit.configure(command=self.onbtn_edit)
        self.btn_delete = ttk.Button(self.frm_constraint_editing)
        self.btn_delete.configure(text="Delete")
        self.btn_delete.grid(column=0, padx=5, pady=5, row=0, sticky="w")
        self.btn_delete.configure(command=self.onbtn_delete)
        self.button8 = ttk.Button(self.frm_constraint_editing)
        self.button8.configure(text="New Constraint")
        self.button8.grid(column=1, padx=5, pady=5, row=1, sticky="e")
        self.button8.configure(command=self.onbtn_newconstr)
        self.frm_constraint_editing.configure(height=200, width=200)
        self.frm_constraint_editing.grid(column=0, row=1, sticky="ew")
        self.frm_constraint_editing.columnconfigure(0, weight=1)
        self.frm_constraint_editing.columnconfigure(1, weight=1)
        self.frame6 = ttk.Frame(self.frm_constraints)
        self.lb_constraints = tk.Listbox(self.frame6)
        self.lb_constraints.configure(height=25, selectmode="extended", width=35)
        self.lb_constraints.grid(column=0, row=0, sticky="nsew")
        self.scrollbar1 = ttk.Scrollbar(self.frame6)
        self.scrollbar1.configure(orient="vertical")
        self.scrollbar1.grid(column=1, row=0, sticky="ns")
        self.frame6.configure(height=200, width=200)
        self.frame6.grid(column=0, row=0)
        self.frm_constraints.configure(height=300)
        self.frm_constraints.grid(column=0, row=1, sticky="nsew")
        self.frm_constraints.rowconfigure(0, weight=1)
        self.frm_constraints.columnconfigure(0, weight=1)
        self.frm_info = ttk.Frame(self.top)
        self.lblfrm_info = ttk.Labelframe(self.frm_info)
        self.label3 = ttk.Label(self.lblfrm_info)
        self.label3.configure(
            text="Make sure to set \nyscrollcommand of listbox and\n.config(command=...) for the scrollbar"
        )
        self.label3.grid(column=0, ipadx=5, ipady=5, padx=5, row=0, sticky="nsew")
        self.lblfrm_info.configure(height=200, text="Project Info", width=400)
        self.lblfrm_info.grid(column=0, padx=5, pady=5, row=0, sticky="nsew")
        self.lblfrm_buttons = ttk.Labelframe(self.frm_info)
        self.btn_save = ttk.Button(self.lblfrm_buttons)
        self.btn_save.configure(text="Change obj .csv")
        self.btn_save.grid(column=0, padx=5, pady=5, row=0, sticky="ew")
        self.btn_save.configure(command=self.onbtn_changeobj)
        self.button6 = ttk.Button(self.lblfrm_buttons)
        self.button6.configure(text="Save Project")
        self.button6.grid(column=0, padx=5, pady=5, row=1, sticky="w")
        self.button6.configure(command=self.onbtn_saveproj)
        self.button7 = ttk.Button(self.lblfrm_buttons)
        self.button7.configure(text="Export to .csv")
        self.button7.grid(column=1, padx=5, pady=5, row=0, sticky="e")
        self.button7.configure(command=self.onbtn_exportcsv)
        self.lblfrm_buttons.configure(height=200, text="Options", width=200)
        self.lblfrm_buttons.grid(column=0, padx=5, pady=5, row=1, sticky="nsew")
        self.lblfrm_buttons.columnconfigure(1, weight=1)
        self.frm_info.configure(height=200, width=200)
        self.frm_info.grid(column=1, row=1, sticky="nsew")
        self.frm_info.rowconfigure(0, weight=1)
        self.top.configure(height=200, padding=15, width=200)
        self.top.grid(column=0, row=0)
        self.top.rowconfigure(1, weight=1)

        # Main widget
        self.lb_constraints.config(yscrollcommand=self.scrollbar1.set)
        self.scrollbar1.config(command=self.lb_constraints.yview)

        self.mainwindow = self.top


    def run(self):
        self.mainwindow.mainloop()







    #
    # Bindings
    #

    def onbtn_edit(self):
        print("Edit")

        selected_inds = self.lb_constraints.curselection()
        pprint(selected_inds)

        if len(selected_inds) != 1:
            return
        
        self._transitionToEditing(selected_inds[0])


    def onbtn_delete(self):
        print("Delete")
        selected_inds = list(self.lb_constraints.curselection())

        # Delete largest to smallest
        selected_inds.sort(reverse=True)

        for ind in selected_inds:
            self._updateDeleteConstrGroup(ind)
        self._redrawEverything()


    def onbtn_newconstr(self):
        print("Adding constraint")
        self._updateNewConstrGroup()
        self._redrawConstrListFrame()


    def onbtn_changeobj(self):
        print("Changing objective file")
        self._transitionToObjReplace()


    def onbtn_saveproj(self):
        print("Saving")
        self._updateSaveProject()


    def onbtn_exportcsv(self):
        print("Exporting to csv")
        self._updateExportCSV()







    #
    # Update Calls
    #

    def _updateDeleteConstrGroup (self, constrInd: int) -> None:
        _constrGroupList: List[models.SetupConstraintGroup] = self._passedProjectState.setupList
        print(f"Deleteting {_constrGroupList[constrInd].namePrefix}")
        _constrGroupList.pop(constrInd)

        self._passedProjectState.setupList = _constrGroupList


    def _updateNewConstrGroup (self) -> None:
        print(f"Adding a new constraint")

        _constrGroupList = self._passedProjectState.setupList
        _constrGroupList.append(
            models.SetupConstraintGroup.createEmptySetup(
                self._passedProjectState.varData
            )
        )
        self._passedProjectState.setupList = _constrGroupList


    # TODO: Move so much of this into fileio
    def _updateSaveProject (self) -> None:
        print("Saving project file")

        outputFilepathStr = io_file.getSaveAsFilepath(PROJ_FILES)
        if outputFilepathStr == None:
            return

        projectDataStr = models.toOutputStr(_passedProjectState, models.ProjectState)
        with open(outputFilepathStr, 'w') as outFile:
            outFile.write(projectDataStr)


    def _updateExportCSV (self) -> None:
        print("Exporting to csv")

        outputFilepathStr = io_file.getSaveAsFilepath(CSV_FILES)
        if outputFilepathStr == None:
            return
        io_file.writeToCSV(outputFilepathStr, _passedProjectState)
        
        print(":D File Written")










    #
    # Transition Calls
    #

    def _transitionToEditing (self, constrInd: int) -> None:
        global _constrGroupList, _passedProjectState, _passedRoot
        print(f"Editing {_constrGroupList[constrInd].namePrefix}")

        _passedProjectState.setupList = _constrGroupList

        for child in _passedRoot.winfo_children():
            child.destroy()

        gui_variablefiltering.buildGUI_VariableFiltering(_passedRoot, _passedProjectState, constrInd)


    def _transitionToObjReplace (self) -> None:
        global _passedProjectState, _passedRoot
        print(f"Going to objective file replacement screen")

        _passedProjectState.setupList = _constrGroupList

        for child in _passedRoot.winfo_children():
            child.destroy()
        
        newGui = gui_newcsv.GUINewCSV(_passedRoot, _passedProjectState)
        













    #
    # Redraw Calls
    #

    def _redrawEverything (self) -> None:
        print("Redrawing Everything")

        # Generate global data
        self._constrPerGroup = []
        self._varsConstrainted = []

        for cGroup in self._passedProjectState.setupList:
            fullConstraint = proc.buildConstraintGroup(cGroup, self._passedProjectState.varData)

            self._constrPerGroup.append(len(fullConstraint.equations))

            for eq in fullConstraint.equations:
                for var in eq.leftVars + eq.rightVars:
                    if var not in self._varsConstrainted:
                        self._varsConstrainted.append(var)

        # Redraw buttons
        self._redrawConstrListFrame()
        self._redrawSummaryStats()


    def _redrawConstrListFrame (self) -> None:
        # numItems = self.lb_constraints.
        self.lb_constraints.delete(0, tk.END)

        COLS = ['#d9ead3', '#a4ca93', '#eecbcb', '#ce8d8d', '#e1deee', '#b3adce']
        ERROR = '#CC3333'

        # Render everything
        for ind, constrGroup in enumerate(self._passedProjectState.setupList):
            name = render.trimEllipsisRight(constrGroup.namePrefix, 20)
            numConstrs = self._constrPerGroup[ind]

            constrGroupStr = "%-20s %4d consts" % (name, numConstrs)

            self.lb_constraints.insert(tk.END, constrGroupStr)
            if (numConstrs == 0):
                self.lb_constraints.itemconfig(ind, {"bg": ERROR})
            else:
                self.lb_constraints.itemconfig(ind, {"bg": COLS[(ind // 10) % len(COLS)]})



    def _redrawSummaryStats (self):
        allVars = self._passedProjectState.varData.all_vars

        allConNames = [x.namePrefix for x in self._passedProjectState.setupList]
        duplicateConCames = [x for x in allConNames if allConNames.count(x) > 1]
        duplicateConCames = list(set(duplicateConCames))

        unconVars = set(map(lambda x: "_".join(x), allVars)) - set(map(lambda x: "_".join(x), self._varsConstrainted))
        unconVars = list(unconVars)

        # Build the summary string
        summaryStr = ""

        totConstrs = sum(self._constrPerGroup)
        totUnConVars = len(unconVars)
        totVarsUsed = len(allVars) - totUnConVars

        summaryStr += f'Constraint Groups: {len(self._constrPerGroup)}\n'
        summaryStr += f'Constraints: {totConstrs}\n'
        summaryStr += f'Variables Used: {totVarsUsed}\n'
        summaryStr += f'Variables Not Used: {totUnConVars}'

        # display duplicate named constraint groups
        if len(duplicateConCames) != 0:
            summaryStr += "\n\n\n == WARNING ==\n"
            summaryStr += f"Duplicate Constriant Names:\n"
            summaryStr += ", ".join(duplicateConCames)

        # display unconstrained variables
        if len(unconVars) != 0:
            summaryStr += "\n\n\n == WARNING ==\n"

            NUM_UNCON_TO_SHOW = 10
            if len(unconVars) > NUM_UNCON_TO_SHOW:
                summaryStr += f'First {NUM_UNCON_TO_SHOW} '
                unconVars = unconVars[:NUM_UNCON_TO_SHOW]
            summaryStr += 'unconstrained variables:\n'
            summaryStr += ", ".join(unconVars)

        # Update
        self.label3.configure(text=summaryStr)








if __name__ == "__main__":
    projState = devtesting.dummyProjectState()

    root = tk.Tk()
    app = ProjectoverviewNewApp(root, projState)
    app.run()


