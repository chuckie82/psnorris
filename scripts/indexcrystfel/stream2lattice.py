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

def stream2lattice(path_stream, path_write, detDistance):
    icrystal = [[detDistance]*6 ]
    f = open(path_stream,'r')
    content = f.readlines()
    f.close()
    for i, val in enumerate(content):
        if (val[:15] == 'Cell parameters'):
            temp = val.split(' ')
            cry_a = float(temp[2])
            cry_b = float(temp[3])
            cry_c = float(temp[4])
            cry_alpha = float(temp[6])
            cry_beta = float(temp[7])
            cry_gamma = float(temp[8])
            icrystal.append([cry_a, cry_b, cry_c, cry_alpha, cry_beta, cry_gamma])
            print cry_a, cry_b, cry_c, cry_alpha, cry_beta, cry_gamma

    icrystal = np.array(icrystal)

    print "####"
    print icrystal

    f = h5py.File(path_write, 'w')
    data_write = f.create_dataset('lattice', icrystal.shape)
    data_write[...] = icrystal
    f.close()
    print "f: ", path_write

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

for idx in np.arange(istart, iend):
	newclen = (clen+stepSize*idx)/1000.
	print '### new clen = ', newclen

	path_stream = os.path.join(para.pathcxi, str(para.experimentName) + '_' + str(para.run).zfill(4)+ '_'+str(idx)+'.stream')
	path_write = os.path.join(para.newgeom, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(idx).zfill(2)+'.h5')
        print "path_stream: ", path_stream
        print "path_write: ", path_write

	if not os.path.exists(path_stream): continue

	detDistance = newclen + para.coffset
	stream2lattice(path_stream, path_write, detDistance)	
	#os.rename(path_stream, path_stream + '_' + str(idx).zfill(2) + '.finish')






