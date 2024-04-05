import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['baron.exe', 'gmsba_nt.cmd', 'gmsba_nx.exe', 'baronnavvy64.dll', 'pthreadVC2-tof.dll', 'optbaron.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'BARON 1001 5 BA 1 0 1 LP MIP RMIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsba_nt.cmd\ngmsba_nx.exe'
