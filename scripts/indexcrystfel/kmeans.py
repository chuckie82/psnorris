import numpy as np
from sklearn.cluster import KMeans
import subprocess
from indexparameter import *
import os

def equals(a, b, eps=0.5):
	if abs(a - b) <= eps:
		return True
	else:
		return False

def is90(a, eps=0.5):
	if abs(a - 90) <= eps:
		return True
	else:
		return False

def is120(a, eps=0.5):
	if abs(a - 120) <= eps:
		return True
	else:
		return False

def getLikeliCentering(clusterCentering):
	print "$$$$: ", clusterCentering
	uniqueCentering = np.unique(clusterCentering)
	print "cen: ", uniqueCentering
	likeliCentering = None
	maxCount = 0
	for i in uniqueCentering:
		if len(np.where(clusterCentering==i)[0]) > maxCount:
			likeliCentering = i.split('\n')[0]
	return likeliCentering

para = experipara()
eps = (2, 1.5) # (Angstrom, degree)
istart = -int((para.numDeltaZ-1)/2)
iend = -istart + 1
skewdata = np.zeros((para.numDeltaZ, 8))
nuc = np.zeros((para.numDeltaZ, 6))
centering = np.zeros((para.numDeltaZ, 1))
bestCenteringList = []

for idx in np.arange(istart, iend):
	myCentering = None
	niggliLattice = np.load('niggli'+str(idx)+'.npy')

	# read centering
	fname = os.path.join(para.newgeom, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(idx).zfill(2)) + '_centering.npy'
	cen = np.load(fname)
	
	if 0:
		import matplotlib.pyplot as plt
		for i in range(6):
			plt.subplot(2,3,i+1)
			plt.hist(niggliLattice[:,i],200)
		plt.show()

	for i in np.arange(0,6):
		X = niggliLattice[:,i]
		X.shape = (len(X),1)
		kmeans = KMeans(n_clusters=2).fit(X)
		print "###", kmeans.cluster_centers_
		diff = abs(kmeans.cluster_centers_[0] - kmeans.cluster_centers_[1])
		if diff >= eps[0]:
			ind = np.where(kmeans.labels_==0)
			print "two cluster"
			mean_uc = np.nanmean(niggliLattice[ind,i])
			median_uc = np.nanmedian(niggliLattice[ind, i])
	    		std_uc = np.nanstd(niggliLattice[ind, i])
			skewdata[idx-istart, i] = 3*(mean_uc - median_uc)/std_uc
			if is120(kmeans.cluster_centers_[0]) or is120(kmeans.cluster_centers_[1]):
				nuc[idx, i] = 120
			elif is90(kmeans.cluster_centers_[0]) or is90(kmeans.cluster_centers_[1]):
				nuc[idx, i] = 90
			else:
				nuc[idx, i] = kmeans.cluster_centers_[0]
			if myCentering is None:
				myCentering = getLikeliCentering(cen[ind])
				bestCenteringList.append(myCentering)
		else:
			print "one cluster"
			mean_uc = np.nanmean(niggliLattice[:,i])
			median_uc = np.nanmedian(niggliLattice[:, i])
	    		std_uc = np.nanstd(niggliLattice[:, i])
			skewdata[idx-istart, i] = 3*(mean_uc - median_uc)/std_uc
			if is120(kmeans.cluster_centers_[0]) or is120(kmeans.cluster_centers_[1]):
				nuc[idx, i] = 120
			elif is90(kmeans.cluster_centers_[0]) or is90(kmeans.cluster_centers_[1]):
				nuc[idx, i] = 90
			else:
				nuc[idx, i] = np.mean(kmeans.cluster_centers_)
			if myCentering is None:
				myCentering = getLikeliCentering(cen)
				bestCenteringList.append(myCentering)
	skewdata[idx-istart, 6] = np.mean(np.abs(skewdata[idx-istart, 0:3]))
	print '### likeli centering', myCentering
	print '### skew a,b,c,alpha, beta, gamma = ', skewdata[idx-istart]
	print '### average skew = ',skewdata[idx-istart, 6] , '\n\n'
	
temp = skewdata[:,6].copy()
index = np.argmin(temp)
para.geom = os.path.join(para.newgeom, 'clen_'+str(index+istart).zfill(2)+'.geom')

print 'Best clen = ', skewdata[index, 7]
print 'Best Geom File: ', para.geom
print 'Best nuc: ', nuc[index,:]
print 'Best centering: ', bestCenteringList[index]
np.save('bestNiggli.npy', nuc[index,:])
np.save('bestCentering.npy', bestCenteringList[index])


