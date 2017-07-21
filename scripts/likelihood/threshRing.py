import psana
import numpy as np
import time
import matplotlib.pyplot as plt
import h5py
import os, sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("exprun", help="psana experiment/run string (e.g. exp=xppd7114:run=43)")
parser.add_argument("areaDetName", help="psana area detector name from 'print evt.keys()' (e.g. cspad)")
args = parser.parse_args()

experimentName = args.exprun.split(':')[0].split('=')[-1]
runNumber = args.exprun.split('=')[-1]
detInfo = args.areaDetName
evtNum = 0

ds = psana.DataSource('exp='+experimentName+':run='+runNumber+':idx')
run = ds.runs().next()
det = psana.Detector(detInfo)
times = run.times()
env = ds.env()
eventTotal = len(times)
evt = None
counter = 0
while evt is None:
    evt = run.event(times[counter]) # guarantee we have a valid event
    counter += 1
psanaMask = det.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True)
#print psanaMask.shape
"""
if eventTotal > 100:
    eventTotal = 100
meanCalib = None
for evtNum in range(eventTotal):
    evt = run.event(times[evtNum])
    calib = det.calib(evt)
    if meanCalib is None:
        meanCalib = calib
    else:
        meanCalib += calib
meanCalib = meanCalib/eventTotal
"""
meanCalib = np.load('mean_img_'+experimentName+'_'+runNumber+'_unassem.npy')
meanCalib1D = meanCalib.ravel()

plt.imshow(det.image(evt,meanCalib),vmax=500,vmin=0)
plt.show()
 
cx, cy     = det.indexes_xy(evt)
ipx, ipy   = det.point_indexes(evt, pxy_um=(0,0))
#print cx, cy
#print ipx, ipy
r = np.sqrt((cx-ipx)**2 + (cy-ipy)**2).ravel().astype(int)

plt.imshow(det.image(evt,np.sqrt((cx-ipx)**2 + (cy-ipy)**2)))
plt.show()

startR = 0
endR = np.max(r)

profile = np.zeros(endR-startR,)
for i, val in enumerate(np.arange(startR,endR)):
    ind = np.where(r==val)[0].astype(int)
    if len(ind) > 0:
        profile[i] = np.mean(meanCalib1D[ind])

myThreshInd = np.argmax(profile)

print myThreshInd
#print myThreshInd, profile[myThreshInd]

plt.plot(profile,'x-')
plt.show()

thickness = 10
indLo = np.where(r>=myThreshInd-thickness/2.)[0].astype(int)
indHi = np.where(r<=myThreshInd+thickness/2.)[0].astype(int)


ind = np.intersect1d(indLo, indHi)
#ind = np.where(r==myThreshInd)[0].astype(int)

np.save("/reg/d/psdm/cxi/cxitut13/res/autosfx/threshRing_"+experimentName+"_"+runNumber+".npy", ind)



folder = os.getcwd()
all_file = os.listdir(folder)
file_num = [0]
for each in all_file:
    if each[:8] == 'thrlist_':
        file_num.append(int(each[-7:-3]))
ofilename = np.amax(file_num) + 1
pathwr = os.path.join(folder, 'thrlist_'+str(ofilename).zfill(4)+'.h5')
f = h5py.File(pathwr,'w')
datawr = f.create_dataset('thrlist', (eventTotal, 4), dtype='i8')
datawr[...] = -np.ones((eventTotal, 4)).astype('i8')
f.close()
for evtNum in range(eventTotal):
    evt = run.event(times[evtNum])
    if evt is None: continue
    tic = time.time()
    calib1D = (psanaMask*det.calib(evt)).ravel()

    temp = calib1D[ind]
    index = np.where(temp>1)
    if index[0].shape[0]==0: continue

    temp = temp[index].copy()
    thresh = np.mean(temp)
    spread = np.std(temp)
    toc = time.time()
    print "time: ", toc-tic
    print 'event:', evtNum, ' --- ', thresh, spread

    thr_low = thresh
    thr_high = max(thresh+spread*2, 2*thresh)
    atot_thr = thr_low+thr_high+spread

    f = h5py.File(pathwr, 'r+')
    f[f.keys()[0]][evtNum, 0:4] = [evtNum, thr_low, thr_high, atot_thr]
    f.close()
    #plt.imshow(det.image(evt),vmax=thresh,vmin=0)
    #plt.title('threshold: '+str(thresh)+' '+str(spread))
    #plt.show()

















