import numpy as np
import h5py
import os, sys
from numba import jit
from scipy import signal
from iparameter import *
from scipy.spatial.distance import cdist
from scipy.spatial import distance


def ireader(ipath):
	if ipath[-3:] == '.h5':
		ifile = h5py.File(ipath, 'r')
		idata = np.array(ifile[ifile.keys()[0]])
		idata = idata.astype('i8')
		ifile.close()
	elif ipath[-4:] == '.npy':
		idata = np.load(ipath)
		idata = idata.astype('i8')
	else:
		raise ValueError('no files found ... ') 
		return [0, False]

	iindex = np.where(idata[:,0]>=0)
	idata = idata[iindex].copy()
	return [idata, True]

@jit
def calculate_likelihood(qPeaks):

    nPeaks = int(qPeaks.shape[1])
    selfD = distance.cdist(qPeaks.transpose(), qPeaks.transpose(), 'euclidean')
    #sortedIndexD = np.argsort(selfD, axis = 1)
    sortedSelfD = np.sort(selfD)
    closestNeighborDist = sortedSelfD[:,1]
    meanClosestNeighborDist = np.median(closestNeighborDist)
    numclosest = [0]*nPeaks
    closestPeaks = [None]*nPeaks
    coords = qPeaks.transpose()
    pairsFound = 0.

    for ii in range(nPeaks):
        index = np.where(selfD[ii,:] == closestNeighborDist[ii])
        #numclosest[ii] = index[0].shape[0]
        closestPeaks[ii] = coords[list(index[0]),:].copy()
        p = coords[ii,:]
        flip = 2*p - closestPeaks[ii]
        d = distance.cdist(coords, flip, 'euclidean')
        sigma = closestNeighborDist[ii]/4.
        mu = 0.
        bins = d
        vals = np.exp( -(bins - mu)**2 / (2. * sigma**2))
        weight = np.sum( vals )  
        pairsFound += weight

    pairsFound = pairsFound / 2.
    pairsFoundPerSpot = pairsFound/float(nPeaks)
    
    return [meanClosestNeighborDist, pairsFoundPerSpot]

def iwriter(ioutput):
	folder = os.getcwd()
	all_file = os.listdir(folder)
	file_num = [0]
	for each in all_file:
		if each[:18] == 'likelihood_output_':
	    		file_num.append(int(each[-7:-3]))
	new_name = np.amax(file_num) + 1
	path_result = os.path.join(os.getcwd(), 'likelihood_output_' + str(new_name).zfill(4) + '.h5')
	f = h5py.File(path_result,'w')
	data_write = f.create_dataset('likeli', ioutput.shape, dtype='i8')
	data_write[...] = ioutput
	f.close()
