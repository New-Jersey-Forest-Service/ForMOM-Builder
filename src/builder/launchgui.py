'''
gui_main.py

This file launches the program
'''

import os
import pathlib
import tkinter as tk
from tkinter import ttk

import builder.gui_mainmenu as gui_mainmenu
import builder.models as models


def main():
	print("Hi")
	# Very important to instantiate the object so it can be passed arround
	projectState = models.ProjectState.createEmptyProjectState()

	root = tk.Tk()
	root.minsize(width=400, height=400)
	root.option_add("*tearOff", False)

	# Load Theme info
	# The forest theme honestly just seems too bright with a GUI not designed for it
	# If I ever redesign the program then I'll use it but for now nah
	# style = ttk.Style(root)
	# themepath = pathlib.Path(__file__).parent.joinpath('../theme/forest-light.tcl').absolute()
	# root.tk.call("source", themepath)
	# style.theme_use('forest-light')

	gui_mainmenu.buildGUI_OpeningScreen(root, projectState)

	root.mainloop()



if __name__ == '__main__':
	main()
