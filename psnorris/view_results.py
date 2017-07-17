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
      cPMan = cctbxPlayMan("cxid9114", 100, trialCount, '', 'optims', '', 0)
      cPMan.buildPlayground(replaceDir=False)
      print cPMan.playground
      cPManList.append(cPMan)
    # Initialize 
    pFOMan = peakFindingOptimizerMan(kwargs['exp'], kwargs['run_no'], [])
    skewList, indexCntList = pFOMan.calcUCDistrSkew(cPManList)
    print "Results:"
    print "A       B       C       Alpha   Beta    Gamma"
    for dist in skewList:
      for param in dist:
        param = str(param)
        if param[0] == "-":
          param = param[:7]
        else:
          param = param[:6]
        diff = 7 - len(param)
        for i in range(diff):
          param = param + " "
        print param,
      print

      
    print indexCntList
    


if __name__ == "__main__":
  view_results(sys.argv[1], window_size=2, step_size=0.2, detz_offset=589, exp=None, run_no=100)


