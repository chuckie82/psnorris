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
	uniqueCentering = np.unique(clusterCentering)
	likeliCentering = None
	maxCount = 0
	for i in uniqueCentering:
		if len(np.where(clusterCentering==i)[0]) > maxCount:
			likeliCentering = i.split('\n')[0]
		maxCount = len(np.where(clusterCentering==i)[0])

	return likeliCentering

para = experipara()
para.pathcxi = os.path.join(para.outDir, 'r'+str(para.run).zfill(4) )
eps = (5, 5, 5, 1.5, 1.5, 1.5) # (Angstrom, degree)
stepSize = 2 # mm
istart = -int((para.numDeltaZ-1)/2)
iend = -istart + 1
skewdata = np.zeros((para.numDeltaZ, 8))
nuc = np.zeros((para.numDeltaZ, 6))
centering = np.zeros((para.numDeltaZ, 1))
bestCenteringList = ['None']*para.numDeltaZ
pdbexist = False
if isinstance(para.pdb, str) and os.path.exists(para.pdb):
	pdbexist = True

for idx in np.arange(para.numDeltaZ):
	myCentering = None
	
	fniggli = para.pathcxi+'/niggli_'+str(idx+istart).zfill(2)+'.npy'
	if para.userslattice:
		fniggli = para.pathcxi+'/niggli_users_'+str(idx+istart).zfill(2)+'.npy'      # users niggli file
	niggliLattice = np.load(fniggli)

	# read centering
	fname = os.path.join(para.pathcxi, str(para.experimentName) + '_' + str(para.run).zfill(4) + '_' + str(idx+istart).zfill(2)) + '_centering.npy'
	cen = np.load(fname)
	
	print '@@@ niggli file: ', fniggli
	print '@@@ centering: ', fname

	skewdata[idx, 7] = (para.coffset+stepSize*(idx+istart)/1000.)

	if True:
		import matplotlib.pyplot as plt
                ptitle = ['a','b','c','al','be','ga']
		for i in range(6):
			plt.subplot(2,3,i+1)
			plt.hist(niggliLattice[:,i],200)
                        plt.title(ptitle[i])
		plt.show()

	for i in np.arange(0,6):
		X = niggliLattice[:,i]
                if len(X) > 10:
                    X.shape = (len(X),1)
		    kmeans = KMeans(n_clusters=2).fit(X)
		    print "###", kmeans.cluster_centers_
		    diff = abs(kmeans.cluster_centers_[0] - kmeans.cluster_centers_[1])

		    if (diff < eps[i]) or pdbexist or para.userslattice:
			    print "one cluster"
			    mean_uc = np.nanmean(niggliLattice[:,i])
			    median_uc = np.nanmedian(niggliLattice[:, i])
	    		    std_uc = np.nanstd(niggliLattice[:, i])
			    skewdata[idx, i] = 3*(mean_uc - median_uc)/std_uc
			    if i in [3,4,5]: 
			    	if is120(kmeans.cluster_centers_[0]) or is120(kmeans.cluster_centers_[1]):
				    nuc[idx, i] = 120    
			    	elif is90(kmeans.cluster_centers_[0]) or is90(kmeans.cluster_centers_[1]):
				    nuc[idx, i] = 90
				else:
				    nuc[idx, i] = mean_uc
			    else:
				    # nuc[idx, i] = np.mean(kmeans.cluster_centers_)
				    nuc[idx, i] = mean_uc
			    if myCentering is None:
				    myCentering = getLikeliCentering(cen)
				    #bestCenteringList.append(myCentering)
				    bestCenteringList[idx] = myCentering

		    else:
	 	    	    ind0 = np.where(kmeans.labels_==0)
		    	    ind1 = np.where(kmeans.labels_==1)
		    	    num0 = ind0[0].shape[0]
		    	    num1 = ind1[0].shape[0]
		    	    if  num0 > num1: 
				ind = ind0
				ilabel = 0
		    	    else: 
				ind = ind1
				ilabel = 1

			    print "two cluster: ", num0,'/',num1, ' ### ', ilabel,'*',ind[0].shape[0]

			    mean_uc = np.nanmean(niggliLattice[ind,i])
			    median_uc = np.nanmedian(niggliLattice[ind, i])
	    		    std_uc = np.nanstd(niggliLattice[ind, i])
			    skewdata[idx, i] = 3*(mean_uc - median_uc)/std_uc
			    if i in [3,4,5]: 
			    	if is120(kmeans.cluster_centers_[0]) or is120(kmeans.cluster_centers_[1]):
				    nuc[idx, i] = 120   
			    	elif is90(kmeans.cluster_centers_[0]) or is90(kmeans.cluster_centers_[1]):
				    nuc[idx, i] = 90
				else:
				    nuc[idx, i] = kmeans.cluster_centers_[ilabel]
			    else:
				    nuc[idx, i] = kmeans.cluster_centers_[ilabel]
			    if myCentering is None:
				    myCentering = getLikeliCentering(cen[ind])            # seems doesn't work
				    #bestCenteringList.append(myCentering)
				    bestCenteringList[idx] = myCentering


        if len(X) > 10:      # why it's len(X)>0
	        skewdata[idx, 6] = np.mean(np.abs(skewdata[idx, 0:3]))
        else:
                skewdata[idx, 6] = 999.
	print '### likeli centering', myCentering
	print '### skew a, b, c, alpha, beta, gamma = ', np.around(skewdata[idx],3)
	print '### average skew = ', np.around(skewdata[idx, 6],3) , '\n\n'
	
temp = skewdata[:,6].copy()
index = np.argmin(temp)
print "skew: ", np.around(temp,3), ' idx=', index
print "saving: ", os.path.join(para.pathcxi, 'coffset_'+str(index+istart).zfill(2)+'.geom')
para.geom = os.path.join(para.pathcxi, 'coffset_'+str(index+istart).zfill(2)+'.geom')

print "nuc: \n", np.around(nuc, 3)

print 'Best coffset = ', np.around(skewdata[index, 7],3)
print 'Best Geom File: ', para.geom
print 'Best nuc: ', np.around(nuc[index,:], 3)
print 'Best centering: ', bestCenteringList[index]
np.save(para.pathcxi+'/bestNiggli.npy', nuc[index,:])
np.save(para.pathcxi+'/bestCentering.npy', bestCenteringList[index])


