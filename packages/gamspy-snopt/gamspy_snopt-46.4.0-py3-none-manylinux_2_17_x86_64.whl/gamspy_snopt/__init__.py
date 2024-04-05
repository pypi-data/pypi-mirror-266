import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libsnlcclib64.so', 'optsnopt.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SNOPT 1 0 SN 1 0 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibsnlcclib64.so snl 1 1'
