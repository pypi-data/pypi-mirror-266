import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libhiscclib64.dylib', 'opthighs.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'HIGHS 11 5 HI 1 0 2 LP MIP RMIP\ngmsgenus.run\ngmsgenux.out\nlibhiscclib64.dylib his 1 1'
