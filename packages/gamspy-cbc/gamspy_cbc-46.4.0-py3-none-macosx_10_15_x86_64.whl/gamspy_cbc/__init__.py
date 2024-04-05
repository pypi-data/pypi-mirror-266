import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libcbccclib64.dylib', 'optcbc.def', 'libiomp5.dylib', 'libmkl_gams.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CBC 2011 5 0001020304050607 1 0 2 LP MIP RMIP\ngmsgenus.run\ngmsgenux.out\nlibcbccclib64.dylib cbc 1 0'
