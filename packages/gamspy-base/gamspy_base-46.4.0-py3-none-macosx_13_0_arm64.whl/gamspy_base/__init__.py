import os
from pathlib import Path

from .version import __version__

directory = str(Path(__file__).resolve().parent)

available_solvers = ['NLPEC', 'SBB', 'CONOPT', 'CONVERT', 'CPLEX', 'PATH', 'BARON', 'CBC', 'CONOPT3', 'COPT', 'DICOPT', 'GUROBI', 'HIGHS', 'IPOPT', 'IPOPTH', 'KNITRO', 'MINOS', 'MPSGE', 'MOSEK', 'SCIP', 'SHOT', 'SNOPT']

files = ['libgmdcclib64.dylib', 'gevopt.def', 'libgsscclib64.dylib', 'gmsprmun.txt', 'libptccclib64.dylib', 'gamserrs.txt', 'libcplex2211.dylib', 'libconopt464.dylib', 'libcvdcclib64.dylib', 'libcpxcclib64.dylib', 'libcplex.dylib', 'libgmszlib164.dylib', 'gmscmpun.txt', 'libguccclib64.dylib', 'gamsstmp.txt', 'libgdxdclib64.dylib', 'gamscmex.out', 'gamslice.txt', 'libgfortran.5.dylib', 'optsbb.def', 'gmsgenux.out', 'gmscvnux.out', 'gmssb_us.run', 'optpath.def', 'libgdxcclib64.dylib', 'libjoatdclib64.dylib', 'libdctmdclib64.dylib', 'eula.pdf', 'gmssb_ux.out', 'gmscvnus.run', 'gmsgenus.run', 'optgams.def', 'optcplex.def', 'liboptdclib64.dylib', 'libpath50.dylib', 'libquadmath.0.dylib', 'libgcc_s.1.1.dylib', 'libgomp.1.dylib', 'optconopt.def', 'optnlpec.def', 'gams', 'libco4cclib64.dylib', 'optconvert.def']

file_paths = [directory + os.sep + file for file in files]
