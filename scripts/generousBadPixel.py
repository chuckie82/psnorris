from psana import *
import numpy as np 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("exprun", help="psana experiment/run string (e.g. exp=xppd7114:run=43)")
parser.add_argument("-n", "--noe", help="number of minimum bad pixels", type=int)
args = parser.parse_args()
n = args.noe

runNum = int(args.exprun.split('=')[-1])
ds = DataSource(args.exprun)
det = Detector('DscCsPad')
det.do_reshape_2d_to_3d(flag=True)

# Get bad pixel mask
un_img = det.mask(runNum,calib=True,status=True,edges=True,central=True,unbond=True,unbondnbrs=True)
(numAsic, numFs, numSs) = un_img.shape

def bp(n):
    for i in range(numAsic):
        for a in range(numSs):
	    x = np.where(un_img[i,:,a] == 0)
            ind = len(x[0])
	    if ind >= n:
	        un_img[i,:,a]=0
    np.save('generousBadPixelMask.npy', un_img)

bp(n)

