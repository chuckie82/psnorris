# experiment parameters
class experipara(object):
    def __init__(self): 
        self.run = 100
        self.experimentName = 'cxic0415'
        self.detInfo = 'DscCsPad'
	self.numDeltaZ = 7                       # odd number
        self.coffset = 0.582              #@@@       #0.588696
        self.queue = 'psnehq'
        self.chunkSize = 800
        self.indexnoe = -1
	self.outDir = '/reg/d/psdm/cxi/cxic0515/scratch/autosfx/cxic0415'
	self.pdb = None #'/reg/d/psdm/cxi/cxic0415/scratch/zhensu/psocake/strep_more.cell'
	self.userslattice = True

        self.peakMethod = 'cxi'        
        self.intRadius = '3,4,5'
        self.indexingMethod = 'mosflm-noretry'
        self.minPeaks = 15
        self.maxPeaks = 2048
        self.minRes = -1
        self.tolerance = '5,5,5,1.5'
        self.indexsample = 'crystal'
        self.instrument = 'CXI'         #@@@
        self.pixelsize = 0.00011        #@@@
        self.clenEpics = 'DscCsPad_z'     #@@@
        self.logger = 'False'
        self.hitParam_threshold = 15
        self.keepData = 'True'
        self.v = '0'
	self.pathcxi = None



