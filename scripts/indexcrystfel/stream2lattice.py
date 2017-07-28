import time
import psana
import h5py
import random
import os, sys, shlex
import numpy as np
import warnings
from indexparameter import *
import subprocess
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

def stream2lattice(path_stream, path_write, iclen, icoffset):
    icrystal = [] #[[detDistance]*6 ]
    f = open(path_stream,'r')
    content = f.readlines()
    f.close()
    idetDistance = iclen + icoffset
    (cry_a, cry_b, cry_c, cry_alpha, cry_beta, cry_gamma) = (0,0,0,0,0,0)
    (latticeType, centering, uniqueAxis) = (0,0,0)
    latticeTypeList = []
    centeringList = []
    uniqueAxisList = []
    for i, val in enumerate(content):
        if (val[:15] == 'Cell parameters'):
            temp = val.split(' ')
            cry_a = float(temp[2]) * 10.
            cry_b = float(temp[3]) * 10.
            cry_c = float(temp[4]) * 10.
            cry_alpha = float(temp[6])
            cry_beta = float(temp[7])
            cry_gamma = float(temp[8])
            icrystal.append([cry_a, cry_b, cry_c, cry_alpha, cry_beta, cry_gamma])
	elif 'lattice_type' in val:
            latticeTypeList.append(val.split('= ')[-1])
	elif 'centering' in val:
            centeringList.append(val.split('= ')[-1])
	elif 'unique_axis' in val:
	    uniqueAxisList.append(val.split('= ')[-1])

    icrystal = np.array(icrystal)
    if icrystal.shape[0] == 0:
	icrystal.shape = (0,6)

    print "####"
    print path_write+'_latticeType.npy'
    np.save(path_write+'_latticeType.npy', latticeTypeList)
    np.save(path_write+'_centering.npy', centeringList)
    np.save(path_write+'_uniqueAxis.npy', uniqueAxisList)

    f = h5py.File(path_write+'.h5', 'w')
    data_write = f.create_dataset('lattice', icrystal.shape)
    data_write[...] = icrystal
    data_write = f.create_dataset('clen', (1,))
    data_write[...] = iclen
    data_write = f.create_dataset('coffset', (1,))
    data_write[...] = icoffset
    data_write = f.create_dataset('detDistance', (1,))
    data_write[...] = idetDistance
    f.close()
    print "f: ", path_write+'.h5'

para = experipara()
para.pathcxi = os.path.join(para.outDir, 'r'+str(para.run).zfill(4) )
fcxi = os.path.join(para.pathcxi, str(para.experimentName) +'_' +str(para.run).zfill(4)+ '.cxi')

print "cxi: ", fcxi

f = h5py.File(fcxi, 'r')
clen = np.array(f['LCLS']['detector_1']['EncoderValue'])[0]/1000.
f.close()
print 'clen = ', clen, 'm'

stepSize = 2 # mm
istart = -int((para.numDeltaZ-1)/2)
iend = -istart + 1
print 'from ', istart, ' to ', iend

for idx in np.arange(istart, iend):
	newcoffset = (para.coffset + stepSize*idx/1000.)
	print '### new coffset = ', newcoffset

	path_stream = os.path.join(para.pathcxi, str(para.experimentName) + '_' + str(para.run).zfill(4)+ '_'+str(idx).zfill(2)+'.stream')
	path_write = os.path.join(para.pathcxi, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(idx).zfill(2))
        print "path_stream: ", path_stream
        print "path_write: ", path_write

	if not os.path.exists(path_stream): 
		print '### stream file not exist ... '
		continue

	stream2lattice(path_stream, path_write, clen, newcoffset)
	#os.rename(path_stream, path_stream + '_' + str(idx).zfill(2) + '.finish')






