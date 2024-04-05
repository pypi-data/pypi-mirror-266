import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libgrbcclib64.so', 'optgurobi.def', 'libgurobi.so.11.0.1', 'libgurobi.so', 'grbgetkey', 'grbprobe']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'GUROBI 11 5 GUGLGD 1 0 2 LP MIP RMIP NLP DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibgrbcclib64.so grb 1 1'
