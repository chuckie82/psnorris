# experiment parameters
class experipara(object):
    def __init__(self): 
        self.run = 100
        self.experimentName = 'cxic0415'
        self.detInfo = 'DscCsPad'
        self.geom = None
        self.peakMethod = 'cxi'
        self.intRadius = '3,4,5'
        self.indexingMethod = 'mosflm-noretry'
        self.minPeaks = 15
        self.maxPeaks = 2048
        self.minRes = -1
        self.tolerance = '5,5,5,1.5'
        self.outDir = None
        self.sample = 'crystal'
        self.queue = 'psnehq'
        self.chunkSize = 200
        self.noe = -1
        self.instrument = 'CXI'
        self.pixelSize = 0.00011
        self.coffset = 0.588696
        self.clenEpics = 'DscCsPad_z'
        self.logger = 'False'
        self.hitParam_threshold = 15
        self.keepData = 'True'
        self.v = '0'
        self.pdb = '/reg/d/psdm/cxi/cxic0415/scratch/zhensu/psocake/strep_more.cell'
        self.newgeom = '/reg/d/psdm/cxi/cxic0415/res/autosfx/indexcrystfel/info'
        self.path = '/reg/d/psdm/cxi/cxic0415/scratch/yoon82/psocake'
	self.pathcxi = None
        self.numDeltaZ = 3 # odd number



