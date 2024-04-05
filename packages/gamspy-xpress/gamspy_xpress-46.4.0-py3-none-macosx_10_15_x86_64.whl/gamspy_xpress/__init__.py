import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['libxpxcclib64.dylib', 'optxpress.def', 'xpauth.xpr', 'libxprs.dylib', 'libxprl.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'XPRESS 11 5 XPXLXSXX 1 0 2 LP MIP RMIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibxpxcclib64.dylib xpx 1 1'
