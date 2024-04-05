import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['milcclib64.dll', 'optminos.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MINOS 1 0 M5 1 0 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nmilcclib64.dll mil 1 0'
