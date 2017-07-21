from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from psmon import publish
import psmon.plots as psplt
import h5py
import numpy as np
from mpidata import mpidata
from psana import *

def runmaster(args, nClients):
    experimentName = args.exprun.split(':')[0].split('=')[-1]
    runNumber = args.exprun.split('=')[-1]

    ds = DataSource(args.exprun+':idx')
    run = ds.runs().next()
    det1 = Detector(args.areaDetName)
    times = run.times()
    eventTotal = len(times)
    evt = None
    counter = 0
    while evt is None:
        evt = run.event(times[counter]) # guarantee we have a valid event
        counter += 1

    final_max_img = None
    final_mean_img = None
    final_square_img = None
    counter = 0.
    _nClients = nClients

    while _nClients > 0:
        # Remove client if the run ended
        md = mpidata()
        md.recv()

	if final_max_img is None:
		final_max_img = md.max_img
                final_mean_img = md.mean_img
		final_square_img = md.square_img
	else:
		final_max_img = np.maximum(final_max_img, md.max_img)
                final_mean_img = final_mean_img + md.mean_img
		final_square_img = final_square_img + md.square_img
        
	counter = counter + md.small.count
	_nClients -= 1	
    std_img = final_square_img/float(counter) - (final_mean_img/float(counter))**2

    savePowder(args, experimentName, runNumber, counter, det1, final_max_img, evt, final_mean_img, std_img)

def savePowder(args, experimentName, runNumber, counter, det1, final_max_img, evt, final_mean_img, std_img):
    np.save(args.outDir+"/max_img_"+experimentName+"_"+runNumber+"_assem.npy", det1.image(evt, final_max_img))
    np.save(args.outDir+"/max_img_"+experimentName+"_"+runNumber+"_unassem.npy", final_max_img)
    np.save(args.outDir+"/mean_img_"+experimentName+"_"+runNumber+"_assem.npy", det1.image(evt, final_mean_img/counter))
    np.save(args.outDir+"/mean_img_"+experimentName+"_"+runNumber+"_unassem.npy", final_mean_img/counter)
    np.save(args.outDir+"/std_img_"+experimentName+"_"+runNumber+"_assem.npy", det1.image(evt, std_img))
    np.save(args.outDir+"/std_img_"+experimentName+"_"+runNumber+"_unassem.npy", std_img)


