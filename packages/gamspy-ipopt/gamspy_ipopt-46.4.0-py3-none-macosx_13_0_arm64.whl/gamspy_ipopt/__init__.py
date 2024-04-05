import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libipocclib64.dylib', 'libipopt64.dylib', 'optipopt.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'IPOPT 11 5 0001020304050607 1 0 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibipocclib64.dylib ipo 1 1'
