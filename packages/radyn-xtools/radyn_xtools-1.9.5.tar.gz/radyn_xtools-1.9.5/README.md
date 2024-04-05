# radyn_xtools

**radyn_xtools** is a package with Python analysis routines for a grid of M dwarf flare models (Kowalski, Allred, & Carlsson, submitted to AAS journals on 2024 Feb 12) that were calculated with the RADYN code.  The `.fits` files (grid output) can be downloaded through Zenodo.  The dependencies (`numpy`, `plotly`, `matplotlib`, `ipympl`, `notebook`, `astropy`,`scipy`) are installed automatically below.

In a terminal window (assuming the user already has Anaconda):

`conda create --name your_env_name python=3.11`

`conda activate your_env_name`

`pip install radyn_xtools`

(in the previous command, either an underscore or hyphen b/w radyn and xtools will work!)

See the Jupyter notebook `radyn_xtools_Demo.ipynb` for a demonstration on how to use the analysis tools.  This notebook should be in the `your_env_name/site-packages/radyn_xtools/` folder.  To find it, start python and type:

`import radyn_xtools.radyn_xtools as radx`

`radx`

`radyn_xtools_Demo.html' shows what the notebook does without having to start up a Jupyter notebook session.

The only (optional) dependency that is not installed automatically is `ffmpeg`.  One of the cells in the notebook relies on this (but can be skipped).
To install this, activate your environment and then type:

`conda install -c conda-forge ffmpeg`
