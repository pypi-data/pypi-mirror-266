import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

files = ['knxcclib64.dll', 'knitro1400.dll', 'optknitro.def']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'KNITRO 103011 0 KN 1 0 2 LP RMIP NLP MCP MPEC RMPEC CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nknxcclib64.dll knx 1 0'
