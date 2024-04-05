import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['cbccclib64.dll', 'optcbc.def', 'pthreads.dll', 'mkl_gams.dll', 'msvcp140.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CBC 2011 5 0001020304050607 1 0 2 LP MIP RMIP\ngmsgennt.cmd\ngmsgennx.exe\ncbccclib64.dll cbc 1 0'
