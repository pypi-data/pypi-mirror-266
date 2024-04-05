import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libmskcclib64.so', 'libmosek64.so.10.1', 'optmosek.def', 'libtbb.so.12.8', 'libtbb.so.12']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MOSEK 11 5 MKMBML 1 0 2 LP MIP RMIP NLP DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibmskcclib64.so msk 1 1'
