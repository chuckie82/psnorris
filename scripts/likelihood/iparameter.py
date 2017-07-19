
# experiment parameters
class experipara(object):
    def __init__(self): 
        self.exp = 'cxic0415'
        self.det = 'DscCsPad'
        self.run = 100
        self.pixsize = 110e-6                 # meter
        self.phenergy = 12.8                  # keV
        self.detectorDistance = 141.0e-3 #138.6926e-3   # meter
        self.center = [873,882]               # center in detector

        self.algorithm = 1
        self.alg_npix_min = 2
        self.alg_npix_max = 20
        self.alg_amax_thr = 0
        self.alg_atot_thr = 2500
        self.alg_son_min = 7
        self.alg1_thr_low = 400
        self.alg1_thr_high = 1200
        self.alg1_rank = 2
        self.alg1_radius = 2
        self.alg1_dr = 1
        self.streakMask_on = 'False'
        self.streakMask_sigma = 1
        self.streakMask_width = 250
        self.userMask_path = '/reg/d/psdm/cxi/cxic0415/scratch/zhensu/psocake/r0101/mask.npy'
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
        self.minPeaks = 20
        self.maxPeaks = 1000
        self.minRes = -1
        self.clen = -0.450           # meter
	self.line = "psnehq"
	self.numcores = 16

