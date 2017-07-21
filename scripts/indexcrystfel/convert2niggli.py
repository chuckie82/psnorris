import time
import psana
import h5py
import random
import os, sys, shlex
import numpy as np
import warnings
from indexparameter import *
import subprocess
from cctbx import uctbx
from cctbx import crystal
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

para = experipara()
para.pathcxi = os.path.join(para.path, 'r'+str(para.run).zfill(4) )
fcxi = os.path.join(para.pathcxi, str(para.experimentName) +'_' +str(para.run).zfill(4)+ '.cxi')

print "cxi: ", fcxi

f = h5py.File(fcxi, 'r')
clen = np.array(f['LCLS']['detector_1']['EncoderValue'])[0]
f.close()
print 'original clen = ', clen, 'mm'

stepSize = 2 # mm
istart = -int((para.numDeltaZ-1)/2)
iend = -istart + 1
print 'from ', istart, ' to ', iend

def niggli(unitCell, spacegroup):
	uc  =  uctbx.unit_cell( unitCell ) # "51 98 53 89.5 68.3 89.9"
	xs  = crystal.symmetry(uc, spacegroup) # "P21"
	cbop_prim = xs.change_of_basis_op_to_niggli_cell()
	xs1 = xs.change_basis(cbop_prim)
        a = str(xs1.unit_cell().parameters()).split('(')[-1].split(')')[0].split(',')
        nuc = np.zeros(6,)
	for i in range(6):
		nuc[i] = float(a[i])
	return nuc

spacegroup = "P1"
skewdata = np.zeros((para.numDeltaZ, 8))
niggliLattice = None
for idx in np.arange(istart, iend):
	newclen = (clen+stepSize*idx)/1000.
	print '### new clen = ', newclen

	path_h5 = os.path.join(para.newgeom, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(idx).zfill(2)+'.h5')
	print "### path_h5: ", path_h5

	if not os.path.exists(path_h5): continue

	detDistance = newclen + para.coffset
	f = h5py.File(path_h5, 'r')
	lattice = np.array(f[f.keys()[0]])
	niggliLattice = np.zeros((lattice.shape[0]-1, lattice.shape[1]))
	for i, val in enumerate(lattice):
		if i == 0: continue
		unitCell = ""
		for j in lattice[i,:]:
			unitCell += str(j) + " "
                nuc = niggli(unitCell, spacegroup)
                niggliLattice[i-1,:] = nuc
	
	for ii in range(6):
		mean_uc = np.nanmean(niggliLattice[:,ii])
        	median_uc = np.nanmedian(niggliLattice[:, ii])
    		std_uc = np.nanstd(niggliLattice[:, ii])
		skewdata[idx-istart, ii] = 3*(mean_uc - median_uc)/std_uc
	skewdata[idx-istart, 6] = np.mean(np.abs(skewdata[idx-istart, 0:3]))
	skewdata[idx-istart, 7] = newclen
        f.close()
	print '### skew a,b,c,alpha, beta, gamma = ', skewdata[idx-istart]
	print '### average skew = ',skewdata[idx-istart, 6] , '\n\n'
	print "@@@: ", np.mean(niggliLattice,axis=0)
	print idx
	np.save('niggli'+str(idx)+'.npy', niggliLattice)



