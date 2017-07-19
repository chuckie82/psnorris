from psana import *
import numpy as np
from mpidata import mpidata 

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def runclient(args):
    ds = DataSource(args.exprun+':idx')
    run = ds.runs().next()
    det1 = Detector(args.areaDetName)
    times = run.times()
    eventTotal = len(times)
    
    max_img = None
    mean_img = None
    square_img = None
    counter = 0
    for nevent in xrange(eventTotal):
        if nevent == args.noe : break
        if nevent%(size-1)!=rank-1: continue # different ranks look at different events
	evt = run.event(times[nevent])
        img = det1.calib(evt)

        if img is None: continue

        if max_img is None:
		max_img = img
                mean_img = img
		square_img = img*img
        else: 
		max_img = np.maximum(img, max_img)		
                mean_img = mean_img + img
		square_img = square_img + img*img
        counter += 1
       	#md.small.intensity = intensity
        #if ((nevent)%2 == 0): # send mpi data object to master when desired
    	
    md=mpidata()

    md.addarray('max_img', max_img)      
    md.addarray('mean_img', mean_img)
    md.addarray('square_img', square_img)
    md.small.count = counter

    md.send()
    
    #md.endrun()	
