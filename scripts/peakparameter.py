
# experiment parameters
class experipara(object):
    def __init__(self): 
        self.exp = 'cxic0415'
        self.det = 'DscCsPad'
        self.run = 100
        self.pixsize = 110e-6                 # meter
        self.phenergy = 12.8                  # keV
        self.detectorDistance = 141.0e-3     #138.6926e-3   # meter
        self.center = [873,882]               # center in detector
	self.coffset = 0.5886964

        self.algorithm = 1
        self.alg_npix_min = 2.0
        self.alg_npix_max = 20.0
        self.alg_amax_thr = 0.0
        self.alg_atot_thr = 2500.0
        self.alg_son_min = 7.0
        self.alg1_thr_low = 400.0
        self.alg1_thr_high = 600.0
        self.alg1_rank = 2
        self.alg1_radius = 2
        self.alg1_dr = 1
        self.streakMask_on = 'False'
        self.streakMask_sigma = 1
        self.streakMask_width = 250
        self.userMask_path = '/reg/d/psdm/cxi/cxic0415/scratch/zhensu/psocake/r0101/mask.npy'
	self.logfile = '/reg/d/psdm/cxi/cxic0415/res/autosfx/.%J.log'
	self.outDir = '/reg/d/psdm/cxi/cxic0415/scratch/yoon82/psocake/r0100'
	self.mask = '/reg/d/psdm/cxi/cxic0415/scratch/yoon82/psocake/r0100/staticMask.h5'
        self.psanaMask_on = 'True'
        self.psanaMask_calib = 'True'
        self.psanaMask_status = 'True'
        self.psanaMask_edges = 'True'
        self.psanaMask_central = 'True'
        self.psanaMask_unbond = 'True'
        self.psanaMask_unbondnrs = 'True'
        self.medianBackground = 0      # median background subtraction
        self.medianRank = 5
        self.radialBackground = 0
        self.minPeaks = 15
        self.maxPeaks = 2048
        self.minRes = -1
        self.clen = "DscCsPad_z"           # meter
	self.line = "psnehq"
	self.numcores = 16
	self.noe = 2000
	self.sample = "sample"
	self.instrument = "CXI"
	self.auto = "True"

