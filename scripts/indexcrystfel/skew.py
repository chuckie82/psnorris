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
		mean_uc = np.nanmean(lattice[1:,ii])
        	median_uc = np.nanmedian(lattice[1:, ii])
    		std_uc = np.nanstd(lattice[1:, ii])
		skewdata[idx-istart, ii] = 3*(mean_uc - median_uc)/std_uc
	skewdata[idx-istart, 6] = np.mean(np.abs(skewdata[idx-istart, 0:3]))
	skewdata[idx-istart, 7] = newclen
        f.close()
	print '### skew a,b,c,alpha, beta, gamma = ', skewdata[idx-istart]
	print '### average skew = ',skewdata[idx-istart, 6] , '\n\n'
	print "@@@: ", np.mean(niggliLattice,axis=0)
print "numIndexed: ", niggliLattice.shape

np.save('niggli.npy', niggliLattice)

temp = skewdata[:,6].copy()
index = np.argmin(temp)
para.geom = os.path.join(para.newgeom, 'clen_'+str(index+istart).zfill(2)+'.geom')

print 'Best clen = ', skewdata[index, 7]
print 'Best Geom File: ', para.geom

##########################
# Merge stream as P1
bestStream = os.path.join(para.pathcxi, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(index+istart)+'.stream')
cmd = 'process_hkl -i '+bestStream+' -o temp.hkl -y 1'
print "cmd: ", cmd
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = process.communicate()
print "out: ", out
print "err: ", err

# Convert hkl to mtz
if os.path.isfile('temp.mtz'): os.remove('temp.mtz')
if os.path.isfile('create-mtz.temp.hkl'): os.remove('create-mtz.temp.hkl')
cmd = './create-mtz temp.hkl'
print "cmd: ", cmd
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = process.communicate()
print "out: ", out
print "err: ", err

# Get Laue group likelihood from pointless
cmd = 'pointless hklin temp.mtz'
print "cmd: ", cmd
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = process.communicate()
print "out: ", out
print "err: ", err

# TODO: Generate unit cell
path_h5 = os.path.join(para.newgeom, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(index).zfill(2)+'.h5')
f = h5py.File(path_h5, 'r')
for ii in range(6):
    mean_uc = np.nanmean(lattice[1:,ii])
    print mean_uc
f.close()
exit()

##########################
# Deploy best file
from PSCalib.CalibFileFinder import deploy_calib_file
ds = psana.DataSource('exp=cxic0415:run=100:idx')
run = ds.runs().next()
env = ds.env()
times = run.times()
evt = run.event(times[0])
det = psana.Detector('DscCsPad')

dz = np.mean(det.coords_z(evt)) - float(para.coffset+skewdata[index, 7]) * 1e6 # microns
geo = det.geometry(evt)
geo.move_geo('CSPAD:V1', 0, dx=0, dy=0, dz=-dz)
fname =  para.pathcxi + "/"+str(para.run)+'-end.data'

geo.save_pars_in_file(fname)
calibDir = '/reg/d/psdm/cxi/cxic0415/calib'
cmts = {'exp': para.experimentName, 'app': 'psocake', 'comment': 'best Z geometry'}
print "name: ", det.name
deploy_calib_file(cdir=calibDir, src=str(det.name), type='geometry', run_start=int(para.run), run_end=None, ifname=fname, dcmts=cmts, pbits=0)




