import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['shtcclib64.dll', 'ipopt64.dll', 'mkl_gams.dll', 'msvcp140.dll', 'pthreads.dll', 'gurobi110.dll', 'vcruntime140_1.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SHOT 1001 5 0001020304050607 1 0 2 MINLP MIQCP\ngmsgennt.cmd\ngmsgennx.exe\nshtcclib64.dll sht 1 1'
