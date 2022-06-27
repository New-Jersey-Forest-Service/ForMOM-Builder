'''
gui_main.py

This file launches the program
'''

import tkinter as tk
from enum import Enum, auto, unique
from typing import Dict, List

import gui_mainmenu
import models


def main():
	print("Hi")
	# Very important to instantiate the object so it can be passed arround
	projectState = models.ProjectState.createEmptyprojectState()

	root = tk.Tk()
	root.minsize(width=400, height=400)

	gui_mainmenu.buildOpeningScreen(root, projectState)

	root.mainloop()



if __name__ == '__main__':
	main()
else:
	print("[[ ERROR ]] This file is not meant to be imported")
	num = 1 / 0
