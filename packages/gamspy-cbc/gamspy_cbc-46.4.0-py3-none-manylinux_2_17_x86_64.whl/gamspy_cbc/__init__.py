import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libcbccclib64.so', 'optcbc.def', 'libmkl_gams.so', 'libiomp5.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CBC 2011 5 0001020304050607 1 0 2 LP MIP RMIP\ngmsgenus.run\ngmsgenux.out\nlibcbccclib64.so cbc 1 0'
