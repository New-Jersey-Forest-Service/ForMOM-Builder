# ForMOM Builder
*GUI Application*

GUI Application, Located on dev-optimization branch in [src/optimization/constraint_builder](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/dev-optimization/src/optimization/constraint_builder). The file to run is src/launchgui.py.

![19Week_TwosidedConstrs_Smol](https://user-images.githubusercontent.com/49537988/178080432-701964e5-15b7-4950-bfb8-081804732d44.png)

This program is a generic tool to build constraints. As input you give it an [objective function](https://github.com/New-Jersey-Forest-Service/ForMOM/blob/dev-optimization/src/optimization/constraint_builder/sample_data/minimodel_obj.csv) 
in csv format, and it scrapes the variable names. These variables names are expected to be structured with seperators, eg: '167N_2021_SBNP' has three
tags, '167N', '2021', 'SBNP'. You could for example have a constriant with all variables involving '167N' because it processes with the tags.

The program is under development so there is no usage guide yet. 
**If you want a usage guide or demo**, please don't hesitate to reach out to me at 
[michael.gorbunov@dep.nj.gov](mailto:michael.gorbunov@dep.nj.gov).
You can try it yourself by running launchgui.py and using one of the files in the sample_data folder.

**Credits**: All development by Michael Gorbunov, but a lot of good 
feedback and ideas came from others on the team - specifically Bill, Bernie, and Courtney


## Running

Requirements are in requirements.txt and can be installed with.

