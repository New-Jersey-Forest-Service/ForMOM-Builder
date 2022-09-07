# ForMOM Constraint Builder
*GUI Application*

GUI Application, Located on dev-optimization branch in [src/optimization/constraint_builder](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/dev-optimization/src/optimization/constraint_builder). The file to run is src/launchgui.py.

![19Week_TwosidedConstrs_Smol](https://user-images.githubusercontent.com/49537988/178080432-701964e5-15b7-4950-bfb8-081804732d44.png)

This program is a generic tool to build constraints.
Linear optimization problems are saved as huge matricies. Building them
by hand involves meticulous work in excel, is slow, and error prone.
This constraint builder looks clunky but works well, and lets you
 - Quickly build 100s of constraints with 100s of variables
 - Interchange the variables used as a project develops

**Credits**: All development by Michael Gorbunov, but a lot of good 
feedback and ideas came from others on the team - specifically Bill, Bernie, Lauren, and Courtney


# Running

To run as a user, this directory is not the right place.
Instead, use the .pyz files in the main 
[ForMOM repository software folder](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/main/software), and reference the [wiki](https://github.com/New-Jersey-Forest-Service/ForMOM/wiki).



# Contributing

This section outlines the code base and should help you get up to speed.
It will be a high level overview. For the most part, messiness and slop
is contained within files - the interactions between files is fairly clean,
and you do not need to understand everything to make changes.


## Running (as a developer)
----------
To execute, you must be in the src directory, and execute as a module
```bash
python3 -m builder.file\_to\_launch
```
requirements.txt has the requirements needed to run this. It is also used
by the build script to bundle dependencies (so users don't need to pip install).


## Building
----------
Currently, building is done by running ```build.sh``.
After execution, you'll see a /build/ folder, 
as well as a ForMOM_Builder.pyz file within. 
This is an executable zip which can be sent to users (similar to java .jar).


## File Organization
----------
In src/builder there are a couple files. Here are their purposes
 - **gui_*.py** - One of the screens of the program. They take user input,
present state, and call on other files to do the heavy lifting.
 - **proc_*.py** - A file which does some sort of processing. 
These are the logically intense files.
 - **io_*.py** - Useful functions for io

The couple other files are
 - **launchgui.py** - Launches the gui (calls on other files)
 - **devtesting.py** - Creates dummy state for testing
 - **models.py** - Contains dataclasses which store project data

All files have top level comments explaining their purpose.
Some files can be run on their own which provides useful examples of how to
use the file's functions.
For example, all gui files will launch their screen using dummy project state.




## GUI Logic
----------
When starting out, guis were written from scratch in python. Those
files have functions split up into groups
 - *Update Calls* - Makes change to the state. Usually calls a redraw function at the end
 - *Redraw Calls* - Redraw some dynamic part of the gui
 - *Transition Calls* - Used to transition between different GUIs
 - *Construction Calls* - Build the entire screen's GUI. Most files' main construction call is buildGUI_ScreenName(...)

All global variables related to a specific screen are stored globally but with
underscores in front. This has yet to cause issues but certainly could.

For **gui_newcsv.py**, the gui was made using pygubu-designer
and does not follow this same pattern. Moving forward
I would recommend doing the same, the above guide is to help with tweaking
older files.

To fit into this system, the only functions
needed are transition and construction calls.
Transition calls do 2 things
 - (1) - Destroy all children of the root
 - (2) - Call the construction method of a different screen, passing state and the now clear root



## Data Pipeline & Structure
-------
Why the UI works how it does becomes a lot easier to understand once you look
understand the datastructures. The class in models.py contains all datastructures
for project state, and their comments should help clear up which functions
to be called for what parts of state.

Looking through the calls in the GUI files is a good starting place if
you're really lost.



