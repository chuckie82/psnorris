def launch_peak_finder():

	print ('peak finding and indexing are together ... ')
	
	launch_index()

def launch_index():

	import sys, os
	import subprocess

	experi_name = 'cxic0415'
	out_dir = '/reg/d/psdm/cxi/cxitut13/scratch/zhensu/cctbx_tut/r0101/discovery/dials'
	mp_nproc = 36
	run_queue = 'psnehq'
	out_log = 'True'
	input_dispatcher = 'cctbx.xfel.xtc_process'
	input_target = '/reg/d/psdm/cxi/cxitut13/scratch/zhensu/cctbx_tut/r0101/discovery/target.phil'
	input_trial = 0
	input_run_num = 101
	dispatch_integrate = 'True'
	
	cmd = 'cxi.mpi_submit' + ' ' + 'input.experiment=' + experi_name + ' ' + 'output.output_dir=' + out_dir + ' ' + \
	'mp.nproc=' + str(mp_nproc) + ' ' + 'mp.queue=' + run_queue + ' ' + 'output.split_logs=' + out_log + ' ' + \
	'input.dispatcher=' + input_dispatcher + ' ' + 'input.target=' + input_target + ' ' + 'input.trial=' + str(input_trial) + ' ' + \
	'input.run_num=' + str(input_run_num) + ' ' + 'dispatch.integrate=' + dispatch_integrate

	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

	print "Submitting batch job ---------- \n", cmd



def determine_parameters():


def launch_merge():

	import sys, os
	import subprocess
	
	mp_nproc = 36
	run_queue = 'psnehq'
	input_run_num = 101
	input_target =  '/reg/d/psdm/cxi/cxitut13/scratch/zhensu/cctbx_tut/r0101/discovery/prime.phil'
	out_dir = '/reg/d/psdm/cxi/cxitut13/scratch/zhensu/cctbx_tut/r0101/discovery/dials'
	input_trial = 0
	datapath = out_dir + '/r' + str(input_run_num).zfill(4) + '/' + str(input_trial).zfill(3) + '/out/idx*.pickle'
	cmd = 'prime.run' + ' ' + input_target + ' ' + 'data=' + datapath
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)





