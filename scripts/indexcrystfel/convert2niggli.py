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

print "##################"
	
para = experipara()
para.pathcxi = os.path.join(para.outDir, 'r'+str(para.run).zfill(4) )
fcxi = os.path.join(para.pathcxi, str(para.experimentName) +'_' +str(para.run).zfill(4)+ '.cxi')

#if os.path.exists(para.pdb):
pdbexist = False
if isinstance(para.pdb, str) and os.path.exists(para.pdb):
	print '@@@ pdb file exists, quit niggle ... \n'
	pdbexist = True

def volumefilter(lattice):
    idata = lattice.copy()
    if idata.shape[0] == 0:
	return idata
    V = []
    for ii in range(idata.shape[0]):
        ialpha = idata[ii,3].copy()/180.*np.pi
        ibeta = idata[ii,4].copy()/180.*np.pi
        igamma = idata[ii,5].copy()/180.*np.pi
        ila = idata[ii,0].copy()
        ilb = idata[ii,1].copy()
        ilc = idata[ii,2].copy()
        iVolume = ila*ilb*ilc*np.sqrt(1+2.*np.cos(ialpha)*np.cos(ibeta)*np.cos(igamma)-np.cos(ialpha)**2-np.cos(ibeta)**2-np.cos(igamma)**2)
        V.append(iVolume)
    V = np.array(V)
    np.save('volumelist.npy', V)

    Vmedian = np.nanmedian(V)
    iidx = np.where(V > Vmedian*0.95)
    idata = idata[iidx].copy()
    if idata.shape[0] == 0:
	return idata
    V = V[iidx].copy()
    iidx = np.where(V < Vmedian*1.05)
    idata = idata[iidx].copy()
    return idata
    
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

def NiggleUsers(ilattice):                 # selected by angle SUM
	(ia, ib, ic, ialpha, ibeta, igamma) = ilattice.copy()
	SUM1 = ialpha + ibeta + igamma
	SUM2 = ialpha + 180. - ibeta + 180. - igamma
	SUM3 = 180. - ialpha + ibeta + 180. - igamma
	SUM4 = 180. - ialpha + 180. - ibeta + igamma
	iidx = np.argmin(np.array([SUM1, SUM2, SUM3, SUM4]))
	if iidx == 0:
		return np.array([ia, ib, ic, ialpha, ibeta, igamma])
	if iidx == 1:
		return np.array([ia, ib, ic, ialpha, 180. - ibeta, 180. - igamma])
	if iidx == 2:
		return np.array([ia, ib, ic, 180. - ialpha, ibeta, 180. - igamma])
	if iidx == 3:
		return np.array([ia, ib, ic, 180. - ialpha, 180. - ibeta, igamma])

f = h5py.File(fcxi, 'r')
clen = np.array(f['LCLS']['detector_1']['EncoderValue'])[0]/1000.
f.close()
print 'original clen = ', clen, 'm'

stepSize = 2 # mm
istart = -int((para.numDeltaZ-1)/2)
iend = -istart + 1
print 'from ', istart, ' to ', iend


spacegroup = "P1"
skewdata = np.zeros((para.numDeltaZ, 8))
niggliLattice = None
print "****: ", istart, iend
for idx in np.arange(istart, iend):
        print "!!!!!! idx: ", idx
	newCoffset = (para.coffset+stepSize*idx/1000.)
	print '### new coffset = ', newCoffset

	path_h5 = os.path.join(para.pathcxi, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(idx).zfill(2)+'.h5')
	print "Read h5: ", path_h5

	if not os.path.exists(path_h5): 
    	    print "No such file: ", path_h5
            continue

	#detDistance = newCoffset + clen
	f = h5py.File(path_h5, 'r')
	lattice = np.array(f['lattice'])
	f.close()

	Asize = lattice.shape[0]
	lattice = volumefilter(lattice)              # volume filter
	print 'Volume filter: ',  Asize, '--to--', lattice.shape[0]

	niggliLattice = np.zeros(lattice.shape)
	niggliLattice_users = np.zeros(lattice.shape)
	
        if pdbexist:
		niggliLattice = lattice.copy()
		niggliLattice_users = lattice.copy()
        	print "@@@@ Save niggli: ", para.pathcxi+'/niggli_'+str(idx).zfill(2)+'.npy'
		print "@@@@ Save users niggli: ", para.pathcxi+'/niggli_users_'+str(idx).zfill(2)+'.npy'
		np.save(para.pathcxi+'/niggli_'+str(idx).zfill(2)+'.npy', niggliLattice)
		np.save(para.pathcxi+'/niggli_users_'+str(idx).zfill(2)+'.npy', niggliLattice_users)
		continue

	for i, val in enumerate(lattice):
		unitCell = ""
		for j in lattice[i,:]:
			unitCell += str(j) + " "
                nuc = niggli(unitCell, spacegroup)
                niggliLattice[i,:] = nuc
		niggliLattice_users[i,:] = NiggleUsers(nuc)
	
	#for ii in range(6):
	#	mean_uc = np.nanmean(niggliLattice[:,ii])
        #	median_uc = np.nanmedian(niggliLattice[:, ii])
    	#	std_uc = np.nanstd(niggliLattice[:, ii])
	#	skewdata[idx-istart, ii] = 3*(mean_uc - median_uc)/std_uc
	#skewdata[idx-istart, 6] = np.mean(np.abs(skewdata[idx-istart, 0:3]))
	#skewdata[idx-istart, 7] = newclen
	#print '### skew a,b,c,alpha, beta, gamma = ', skewdata[idx-istart]
	#print '### average skew = ',skewdata[idx-istart, 6] , '\n\n'
	#print "@@@: ", np.mean(niggliLattice,axis=0)
	#print idx
        print "@@@@ Save niggli: ", para.pathcxi+'/niggli_'+str(idx).zfill(2)+'.npy'
	print "@@@@ Save users niggli: ", para.pathcxi+'/niggli_users_'+str(idx).zfill(2)+'.npy'
	np.save(para.pathcxi+'/niggli_'+str(idx).zfill(2)+'.npy', niggliLattice)
	np.save(para.pathcxi+'/niggli_users_'+str(idx).zfill(2)+'.npy', niggliLattice_users)

	if niggliLattice_users.shape[0] == 0:
		print '### No indexed images ... '
		continue
	lattice_users = np.nanmean(niggliLattice_users, axis=0)
	unitCell = ""
	for j in lattice_users:
		unitCell += str(j) + " "
	print '### Users Niggle average: ', np.around( niggli(unitCell, spacegroup), 3)




