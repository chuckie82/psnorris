from psana import *
import numpy as np 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("exprun", help="psana experiment/run string (e.g. exp=xppd7114:run=43)")
parser.add_argument("-d", "--detInfo", help="detector alias (e.g. DscCsPad)", type=str)
parser.add_argument("-n", "--numBad", help="number of minimum bad pixels", default=10, type=int)
parser.add_argument("-o", "--outDir", help="output directory", type=str)
args = parser.parse_args()

runNum = int(args.exprun.split('=')[-1])
ds = DataSource(args.exprun)
det = Detector(args.detInfo)
det.do_reshape_2d_to_3d(flag=True)

# Get bad pixel mask
unassem_img = det.mask(runNum,calib=True,status=True,edges=True,central=True,unbond=True,unbondnbrs=True)
(numAsic, numFs, numSs) = unassem_img.shape

for i in range(numAsic):
    for a in range(numSs):
	x = np.where(unassem_img[i,:,a] == 0)
        ind = len(x[0])
	if ind >= args.numBad:
	    unassem_img[i,:,a]=0

np.save(args.outDir + '/generousBadPixelMask.npy', unassem_img)


