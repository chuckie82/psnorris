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

    icrystal = np.array(icrystal)

    f = h5py.File(path_write, 'w')
    data_write = f.create_dataset('lattice', icrystal.shape)
    data_write[...] = icrystal
    f.close()


def cmdline(para):
    cmd =   "indexCrystals" + \
            " -e " + para.experimentName + \
            " -d " + para.detInfo + \
            " --geom " + str(para.geom) + \
            " --peakMethod " + para.peakMethod + \
            " --integrationRadius " + para.intRadius + \
            " --indexingMethod " + para.indexingMethod + \
            " --minPeaks " + str(para.minPeaks) + \
            " --maxPeaks " + str(para.maxPeaks) + \
            " --minRes " + str(para.minRes) + \
            " --tolerance " + str(para.tolerance) + \
            " --outDir " + str(para.outDir) + \
            " --sample " + para.sample + \
            " --queue " + para.queue + \
            " --chunkSize " + str(para.chunkSize) + \
            " --noe " + str(para.noe) + \
            " --instrument " + para.instrument + \
            " --pixelSize " + str(para.pixelSize) + \
            " --coffset " + str(para.coffset) + \
            " --clenEpics " + para.clenEpics + \
            " --logger " + str(para.logger) + \
            " --hitParam_threshold " + str(para.hitParam_threshold) + \
            " --keepData " + str(para.keepData) + \
	    " -v " + str(para.v) + \
            " --likelihood 0.04"
    if para.pdb: cmd += " --pdb " + para.pdb
    cmd += " --run " + str(para.run)
    return cmd

para = experipara()
para.pathcxi = os.path.join(para.path, 'r'+str(para.run).zfill(4) )
fgeom = os.path.join(para.pathcxi, '.temp.geom')
fcxi = os.path.join(para.pathcxi, str(para.experimentName) +'_' +str(para.run).zfill(4)+ '.cxi')

print "geom: ", fgeom
print "cxi: ", fcxi

f = h5py.File(fcxi, 'r')
clen = np.array(f['LCLS']['detector_1']['EncoderValue'])[0]
f.close()
print 'original clen = ', clen, 'mm'

f = open(fgeom, 'r')
content = f.readlines()
f.close()

stepSize = 2 # mm
start = -1 * int(np.floor(para.numDeltaZ - para.numDeltaZ/2.))
end = int(np.ceil(para.numDeltaZ - para.numDeltaZ/2.))

for idx in np.arange(start, end):
    fgeom_new = os.path.join(para.newgeom, 'clen_'+str(idx).zfill(2)+'.geom')
    print "new geom: ", fgeom_new
    f = open(fgeom_new, 'w')
    for i, val in enumerate(content):
        if val[:6] == 'clen =':
            content[i] = 'clen = ' + str( (clen + stepSize*idx)/1000. ) + '\n'
            break
    f.writelines(content)
    f.close()
print 'new geom files created ... '

for idx in np.arange(start, end):
	newclen = (clen+stepSize*idx)/1000.
	print '### new clen = ', newclen
	para.geom = os.path.join(para.newgeom, 'clen_'+str(idx).zfill(2)+'.geom')
	para.outDir = para.path
	cmd = cmdline(para)
        cmd += " --tag "+str(idx)
	print "Launch indexing job: ", cmd
	p = subprocess.Popen(shlex.split(cmd))

