from cctbxPlay import cctbxPlayMan
from psana import *
from xfel.cxi.cspad_ana import cspad_tbx

class peakFindingOptimizerMan:
  def __init__(self, exp, runNo, eventList, target='target.phil', mask='mask.pickle', qName='psana', nProc=12):
    self.exp = exp
    self.runNo = runNo
    self.eventList = eventList
    self.target = target
    self.mask = mask
    self.qName = qName
    self.nProc = nProc
    # since cctbx only understand timestamp for event filtering
    # converts eventList to tsList
    ds = DataSource('exp='+self.exp+':run='+str(self.runNo)+':idx')
    times = ds.runs().next().times()
    tsList = [cspad_tbx.evt_timestamp((t.seconds(),t.nanoseconds()/1e6)) for i,t in enumerate(times) if i in eventList]
    self.strTs = ' debug.event_timestamp='.join(['']+tsList)
  
  def optimize(self, method='BruteForce', **kwargs):
    if method == 'BruteForce':
      #generate a line search
      windows = range(-int(kwargs['window_size']/2),int(kwargs['window_size']/2))
      detz_offsets = map(lambda x: x*kwargs['step_size']+kwargs['detz_offset'], windows)
      for trialCount, detz_offset in enumerate(detz_offsets):
        # from a given experiment-run-event_list, 
        cPMan = cctbxPlayMan(self.exp, self.runNo, trialCount, self.target, 'optims', self.qName, self.nProc, 
            'format.cbf.invalid_pixel_mask='+self.mask, 'format.cbf.detz_offset='+str(detz_offset),  
            self.strTs)
        cPMan.buildPlayground(replaceDir=True)
        # Index
        cPMan.doIntegrate()
        
