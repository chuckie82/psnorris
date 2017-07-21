import time
import psana
import h5py
import random
import os, sys
import numpy as np
from numba import jit
import psanaWhisperer
from mpi4py import MPI
import PeakFinder as pf
from scipy import signal
from mpidata import mpidata
from scipy.spatial.distance import cdist
from scipy.spatial import distance
import warnings
from ifunction import *
from iparameter import *
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
comm = MPI.COMM_WORLD  
comm_rank = comm.Get_rank()  
comm_size = comm.Get_size() 

# users parameters
class userspara(object):
    def __init__(self): 
        self.reinitial = False    # whether initialize every time
        self.writefile = True     # whether output a file
        self.runMode = 2          # mode1: same thresh for each event, mode2: different thresh for each event
        #self.fevent = os.path.join(os.getcwd(), 'eventlist.h5')

args = experipara()
para = userspara()

# event list columns: 0(event number), 1(thr_low), 2(thr_high), 3(atot_thr)
#[eventlist, imark] = ireader(para.fevent)

ds = psana.DataSource("exp="+args.exp+":run="+str(args.run)+':idx')
run = ds.runs().next()
env = ds.env()
times = run.times()
dt = psana.Detector(args.det)
dt.do_reshape_2d_to_3d(flag=True)
runTotal = len(times)
eventTotal = 2000 #len(times)#eventlist.shape[0]
eventlist = range(eventTotal)

distri = np.linspace(0, eventTotal, comm_size).astype('int')
if comm_rank == 0:
    print 'run Total number = ', runTotal
    print 'event Total number = ', eventTotal
    #print 'event list = ', eventlist[:,0]
else:
    print 'Rank:', comm_rank, ' process: ', distri[comm_rank-1], '/', distri[comm_rank]

iFirst = True
ind = None
if (comm_rank != 0):
    for pevent in range(distri[comm_rank-1], distri[comm_rank]):
        nevent = eventlist[pevent]#, 0]
        evt = run.event(times[nevent])
        detarr = dt.calib(evt)

        imd = mpidata()
        imd.small.eventNum = nevent
        evtId = evt.get(psana.EventId)
        imd.small.seconds = evtId.time()[0]
        imd.small.nanoseconds = evtId.time()[1]
        imd.small.fiducials = evtId.fiducials()

        if detarr is None:      
            imd.small.likeli = 0
            imd.small.nPeaks = 0
            imd.send()
            imd = None
            print 'comm_rank: ', int(comm_rank), '  /event: ',  -1, '  /peaks: ', nPeaks, '  /likeli: ', 0
            continue

        if iFirst:
            ix = dt.indexes_x(evt)
            iy = dt.indexes_y(evt)
            iX = np.array(ix, dtype=np.int64)
            iY = np.array(iy, dtype=np.int64)
            iFirst = False
            # Read in powder pattern and calculate pixel indices
            meanCalib = np.load('/reg/d/psdm/cxi/cxic0415/res/autosfx/mean_img_'+args.exp+'_'+str(args.run)+'_unassem.npy')
            meanCalib1D = meanCalib.ravel() 
            cx, cy     = dt.indexes_xy(evt)
            ipx, ipy   = dt.point_indexes(evt, pxy_um=(0,0))
            r = np.sqrt((cx-ipx)**2 + (cy-ipy)**2).ravel().astype(int)
            startR = 0
            endR = np.max(r)
            profile = np.zeros(endR-startR,)
            for i, val in enumerate(np.arange(startR,endR)):
                ind = np.where(r==val)[0].astype(int)
                if len(ind) > 0:
                    profile[i] = np.mean(meanCalib1D[ind])
            myThreshInd = np.argmax(profile)
            thickness = 10
            indLo = np.where(r>=myThreshInd-thickness/2.)[0].astype(int)
            indHi = np.where(r<=myThreshInd+thickness/2.)[0].astype(int)
            ind = np.intersect1d(indLo, indHi)

        # Initialize hit finding
        #if not hasattr(dt, 'peakFinder') or para.reinitial or (para.runMode==2):
            args.alg1_thr_low = 0.#eventlist[pevent,1]
            args.alg1_thr_high = 0.#eventlist[pevent,2]
            args.alg_atot_thr = 0.#eventlist[pevent,3]
            #print 'event ', nevent, ' is initializing ... with threshold: ', args.alg1_thr_low, '/', args.alg1_thr_high, '/', args.alg_atot_thr
            if args.algorithm == 1:
                dt.peakFinder = pf.PeakFinder(env.experiment(), evt.run(), args.det, evt, dt,
                                            args.algorithm, args.alg_npix_min,
                                            args.alg_npix_max, args.alg_amax_thr,
                                            args.alg_atot_thr, args.alg_son_min,
                                            alg1_thr_low=args.alg1_thr_low,
                                            alg1_thr_high=args.alg1_thr_high,
                                            alg1_rank=args.alg1_rank,
                                            alg1_radius=args.alg1_radius,
                                            alg1_dr=args.alg1_dr,
                                            streakMask_on=args.streakMask_on,
                                            streakMask_sigma=args.streakMask_sigma,
                                            streakMask_width=args.streakMask_width,
                                            userMask_path=args.userMask_path,
                                            psanaMask_on=args.psanaMask_on,
                                            psanaMask_calib=args.psanaMask_calib,
                                            psanaMask_status=args.psanaMask_status,
                                            psanaMask_edges=args.psanaMask_edges,
                                            psanaMask_central=args.psanaMask_central,
                                            psanaMask_unbond=args.psanaMask_unbond,
                                            psanaMask_unbondnrs=args.psanaMask_unbondnrs,
                                            medianFilterOn=args.medianBackground,
                                            medianRank=args.medianRank,
                                            radialFilterOn=args.radialBackground,
                                            distance=args.detectorDistance,
                                            minNumPeaks=args.minPeaks,
                                            maxNumPeaks=args.maxPeaks,
                                            minResCutoff=args.minRes,
                                            clen=args.clen)
        # Calculate peak finding parameters
        calib1D = detarr.ravel()
        thresh = np.mean(calib1D[ind])
        spread = np.std(calib1D[ind])
        thr_high = int(thresh+3.*spread)
        thr_low = int(thresh+2.*spread)

        dt.peakFinder.findPeaks(detarr, evt, thr_high=thr_high, thr_low=thr_low)
        md_peaks = dt.peakFinder.peaks.copy()
        nPeaks = md_peaks.shape[0]
        dt.peakFinder.peaks = None
	#if (para.reinitial) or (para.runMode==2): dt.peakFinder = None

        if (nPeaks<args.minPeaks) or (nPeaks>args.maxPeaks):
            imd.small.likeli = 0
            imd.small.nPeaks = nPeaks
            imd.send()
            imd = None
            #print 'comm_rank: ', int(comm_rank), '  /event: ', nevent, '  /peaks: ', nPeaks, '  /likeli: ', 0
            continue

        cenX = iX[np.array(md_peaks[:, 0], dtype=np.int64), np.array(md_peaks[:, 1], dtype=np.int64), np.array(md_peaks[:, 2], dtype=np.int64)] + 0.5
        cenY = iY[np.array(md_peaks[:, 0], dtype=np.int64), np.array(md_peaks[:, 1], dtype=np.int64), np.array(md_peaks[:, 2], dtype=np.int64)] + 0.5

        x = cenX - args.center[0]
        y = cenY - args.center[1]

        pixSize = float(args.pixsize)
        detdis = float(args.detectorDistance)
        z = detdis/pixSize * np.ones(x.shape) # pixels
        wavelength = 12.407002/float(args.phenergy) # Angstrom
        norm = np.sqrt(x**2 + y**2 + z**2) 
        qPeaks = (np.array([x,y,z])/norm - np.array([[0.],[0.],[1.]]))/wavelength
        [meanClosestNeighborDist, pairsFoundPerSpot] = calculate_likelihood(qPeaks)
        #print 'comm_rank: ', int(comm_rank), '  /event: ', nevent, '  /peaks: ', nPeaks, '  /likeli: ', pairsFoundPerSpot
        print "#####: ", nevent, thr_high, thr_low, nPeaks, pairsFoundPerSpot

        imd.small.nPeaks = nPeaks
        imd.small.likeli = pairsFoundPerSpot
        imd.send()
        imd = None

elif (comm_rank == 0):
    result = np.zeros((6, eventTotal)).astype('i8')
    for ii in range(eventTotal):
        rmd = mpidata()
        rmd.recv()
        result[0,ii] = int(rmd.small.eventNum)
        result[1,ii] = int(rmd.small.nPeaks)
        result[2,ii] = int(1e4*rmd.small.likeli)
        result[3,ii] = int(rmd.small.seconds)
        result[4,ii] = int(rmd.small.nanoseconds)
        result[5,ii] = int(rmd.small.fiducials)
        rmd = None
    temp = result[2,:].copy()
    sortIndex = np.argsort(temp)[::-1]
    output = np.zeros(result.shape).astype('i8')
    for ii in range(temp.shape[0]):
        output[:,ii] = result[:, sortIndex[ii]].copy()

    output = np.transpose(output)

    print '\nFinal result -------------- '
    for ii in range(temp.shape[0]):
        print str(output[ii,0]).rjust(8), str(output[ii,1]).rjust(8), str(output[ii,2]).rjust(8)

    if para.writefile:
        iwriter(output)



