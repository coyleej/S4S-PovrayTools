# RenderTools
POV-Ray tools for use with MANTIS

This repository is a stand-alone development branch for the MANTIS rendering tools. It is actively under development, so some of the scripts may be semi-functional. If you want something that is guaranteed to work, please refer to MANTIS. (MANTIS can be found here: https://github.com/harperes/MANTIS) 

The following is a brief description of what all files here do. For additional details, please refer to the docstrings in the functions.

call_write_POV.py : example for rendering an image of a single device from a MANTIS json file, calls rendering.py

call_gif_POV.py : example for rendering a gif containing a series of devices from a MANTIS json file, calls rendering.py

rendering.py : the POV-Ray function writes a .pov file and renders a .png by default (will eventually a blender function, too)

util.py : the function to extract data from the MANTIS json

util_pov.py : utility functions required by the code in rendering.py

