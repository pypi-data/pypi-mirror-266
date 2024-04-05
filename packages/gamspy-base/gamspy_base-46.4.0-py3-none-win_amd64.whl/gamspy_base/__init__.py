import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

available_solvers = ['NLPEC', 'SBB', 'CONOPT', 'CONVERT', 'CPLEX', 'PATH', 'BARON', 'CBC', 'CONOPT3', 'COPT', 'DICOPT', 'GUROBI', 'HIGHS', 'IPOPT', 'IPOPTH', 'KNITRO', 'MINOS', 'MPSGE', 'MOSEK', 'SCIP', 'SHOT', 'SNOPT', 'XPRESS']

files = ['.uninstinfo.ini', 'co4cclib64.dll', 'conopt464.dll', 'cplex2211.dll', 'cpxcclib64.dll', 'cvdcclib64.dll', 'dctmdclib64.dll', 'eula.pdf', 'gams.exe', 'gamscmex.exe', 'gamserrs.txt', 'gamslice.txt', 'gdxcclib64.dll', 'gevopt.def', 'gmdcclib64.dll', 'gmscmpNT.txt', 'gmscvnnt.cmd', 'gmscvnnx.exe', 'gmsgennt.cmd', 'gmsgennx.exe', 'gmsprmNT.txt', 'gmssb_nx.exe', 'gmszlib164.dll', 'gsscclib64.dll', 'guccclib64.dll', 'joatdclib64.dll', 'libifcoremd.dll', 'libiomp5md.dll', 'libmmd.dll', 'optconopt.def', 'optconvert.def', 'optcplex.def', 'optdclib64.dll', 'optgams.def', 'optnlpec.def', 'optpath.def', 'optsbb.def', 'path50.dll', 'ptccclib64.dll', 'svml_dispmd.dll', 'vcruntime140.dll']

file_paths = [directory + os.sep + file for file in files]
