pyWRF-NMM
=========

Just some scripts for post processing WRF NMM model output in python. Include this scripts in your PATH and execute them when in the directory containing `wrfout*` files.

Dependencies
------------
Required: Numpy, netCDF4, matplotlib, basemap
Optional: ffmpeg

Usage
-----
* `visualize_wrfout.py` will guide you interactively through creating map plots from wrf output data. It supports searching for variables by names and descriptions and choosing a layer when specifying a 4D variable. The `--all-files` command line parameter will run the script for all the `wrfout` files in the working directory at once and creating one png output file per `wrfout` file. It will create the map plot with scaling and coordinates according to your data in lambert conformal projection. Can be adapted for non-NMM WRF models by adjusting for different(ly named) model output files and changing the latitude / longitude variables according to the model. Don't be afraid to change this script according to your needs - it's still below 200 LOC!
* `create_video.sh` (needs ffmpeg) is used to combine all the png files in the working directory into a video. Meant to be used after `visualize_wrfout.py`.
