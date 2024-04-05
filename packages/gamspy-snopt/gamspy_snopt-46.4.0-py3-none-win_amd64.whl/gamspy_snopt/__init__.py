import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['snlcclib64.dll', 'optsnopt.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SNOPT 1 0 SN 1 0 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nsnlcclib64.dll snl 1 0'
