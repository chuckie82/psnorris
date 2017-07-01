from cctbxPlan import cctbxPlaMan
from psana import *
from xfel.cxi.cspad_ana import cspad_tbx

class peakFindingOptimizerMan:
  def __init__(self, exp, runNo, eventList, beamXY, target='target.phil', mask='mask.pickle', nproc=16):
    self.exp = exp
    self.runNo = runNo
    self.eventList = eventList
    self.beamXY = beamXY
    self.target = target
    self.mask = mask
    self.nproc = nproc
    # since cctbx only understand timestamp for event filtering
    # converts eventList to tsList
    ds = DataSource('exp='+self.exp+':run='+str(self.runNo)+':idx')
    times = ds.runs().next().times()
    tsList = [cspad_tbx.evt_timestamp((t.seconds(),t.nanoseconds()/1e6)) for i,t in enumerate(times) if i in eventList]
    self.strTs = ' debug.event_timestamp='.join(['']+tsList)
  
  def optimize(self, method='BruteForce', **kwargs):
    if method == 'BruteForce':
      #generate a line search
      spotSizes = range(kwargs['min_spot_size'], kwargs['max_spot_size'])
      for trialCount, spotSize in enumerate(spotSizes):
        # from a given experiment-run-event_list, change spot size parameter
        cPMan = cctbxPlayMan(exp=self.exp, runNo=self.runNo, trialNo=trialCount, 
            targetPhil=self.target, outputDir='optims', nproc=self.nproc, 
            'spotfinder.filter.min_spot_size='+str(spotSize), self.strTs)
        cPMan.buildPlayground(replaceDir=True)
        # Index
        cPMan.doIndex()
      
      
      
