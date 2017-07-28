from peakparameter import *
import os, sys, shlex
import subprocess

para = experipara()

def cmdline(para):
    cmd =   "bsub" + \
	    " -q " + str(para.line) + \
	    " -n " + str(para.numcores) + \
	    " -o " + str(para.logfile) + \
	    " mpirun findPeaks" + \
	    " -e " + str(para.experimentName) + \
	    " -d " + str(para.detInfo) + \
	    " --outDir " + str(para.outDir) + \
	    " --algorithm " + str(para.algorithm) + \
	    " --alg_npix_min " + str(para.alg_npix_min) + \
	    " --alg_npix_max " + str(para.alg_npix_max) + \
	    " --alg_amax_thr " + str(para.alg_amax_thr) + \
	    " --alg_atot_thr " + str(para.alg_atot_thr) + \
	    " --alg_son_min " + str(para.alg_son_min) + \
	    " --alg1_thr_low " + str(para.alg1_thr_low) + \
	    " --alg1_thr_high " + str(para.alg1_thr_high) + \
	    " --alg1_rank " + str(para.alg1_rank) + \
	    " --alg1_radius " + str(para.alg1_radius) + \
	    " --alg1_dr " + str(para.alg1_dr) + \
	    " --psanaMask_on " + "True" + \
	    " --psanaMask_calib " + "True" + \
	    " --psanaMask_status " + "True" + \
	    " --psanaMask_edges " + "True" + \
	    " --psanaMask_central " + "True" + \
	    " --psanaMask_unbond " + "True" + \
	    " --psanaMask_unbondnrs " + "True" + \
	    " --mask " + str(para.mask) + \
	    " --noe " + str(para.peaknoe) + \
	    " --clen " + str(para.clen) + \
	    " --coffset " + str(para.coffset) + \
	    " --minPeaks " + str(para.minPeaks) + \
	    " --maxPeaks " + str(para.maxPeaks) + \
	    " --minRes " + str(para.minRes) + \
	    " --sample " + str(para.peaksample) + \
	    " --instrument " + str(para.instrument) + \
	    " --pixelSize " + str(para.pixsize) + \
	    " --auto " + str(para.auto) + \
	    " --detectorDistance " + str(para.detectorDistance) + \
	    " -r " + str(para.run)

    return cmd

cmd = cmdline(para)

#ori = 'bsub -q psnehq -n 36 -o /reg/d/psdm/cxi/cxic0415/scratch/yoon82/psocake/r0100/.%J.log mpirun findPeaks -e cxic0415 -d DscCsPad --outDir /reg/d/psdm/cxi/cxic0415/scratch/yoon82/psocake/r0100 --algorithm 1 --alg_npix_min 2.0 --alg_npix_max 20.0 --alg_amax_thr 0.0 --alg_atot_thr 1000.0 --alg_son_min 7.0 --alg1_thr_low 250.0 --alg1_thr_high 600.0 --alg1_rank 2 --alg1_radius 2 --alg1_dr 1 --psanaMask_on True --psanaMask_calib True --psanaMask_status True --psanaMask_edges True --psanaMask_central True --psanaMask_unbond True --psanaMask_unbondnrs True --mask /reg/d/psdm/cxi/cxic0415/scratch/yoon82/psocake/r0100/staticMask.h5 --noe 2000 --clen DscCsPad_z --coffset 0.5886964 --minPeaks 15 --maxPeaks 2048 --minRes -1 --sample sample --instrument CXI --pixelSize 0.00011 --auto True --detectorDistance 0.138693 -r 100'

print 'cmd = ', cmd
p = subprocess.Popen(shlex.split(cmd))



