from cctbxPlay import cctbxPlayMan
from peakFindingOptimizer import peakFindingOptimizerMan
import sys

def view_results(playActivity, **kwargs):
  if playActivity == "peakFinding":
    # generate a line search
    windows = range(-int(kwargs['window_size']/2),int(kwargs['window_size']/2))
    detz_offsets = map(lambda x: x*kwargs['step_size']+kwargs['detz_offset'], windows)
    cPManList = []
    for trialCount, detz_offset in enumerate(detz_offsets):
      # from a given experiment-run-event_list, 
      cPMan = cctbxPlayMan("cxid9114", 0, trialCount, '', 'optims', '', 0)
      cPMan.buildPlayground(replaceDir=False)
      cPManList.append(cPMan)
    # Initialize 
    pFOMan = peakFindingOptimizerMan(kwargs['exp'], kwargs['run_no'], [])
    results = pFOMan.calcUCDistrSkew(cPManList)
    print "Results:"
    for res in results: print res
    
if __name__ == "__main__":
  view_results(sys.argv[1], window_size=2, step_size=0.2, detz_offset=589, exp=None, run_no=0)


