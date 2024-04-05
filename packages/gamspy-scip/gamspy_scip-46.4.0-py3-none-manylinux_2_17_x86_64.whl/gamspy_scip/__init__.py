import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libscpcclib64.so', 'libscip64.so', 'libipopt64.so', 'libmkl_gams.so', 'libiomp5.so', 'libxprl.so.x9.0', 'libxprl-3.2.5-x9.0.so', 'libxprs.so.41', 'libxprs.so.41.01.03', 'libgurobi.so.11.0.1', 'libgurobi.so', 'libbliss64.so', 'libtbb64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SCIP 2001 5 SC 1 0 2 MIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibscpcclib64.so scp 1 1'
