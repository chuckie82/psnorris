#driver for cctbx peakFinding optimizer
from peakFindingOptimizer import peakFindingOptimizerMan
import h5py, sys
import numpy as np

if __name__ == '__main__':
  # Input
  exp = sys.argv[1]
  runNo = int(sys.argv[2])
  eventH5File = sys.argv[3]
  nTopEvents = int(sys.argv[4])
  targetFile = sys.argv[5]
  maskFile = sys.argv[6]
  qName = sys.argv[7]
  nProc = int(sys.argv[8])
  detz_offset = int(sys.argv[9])
  window_size = int(sys.argv[10])
  step_size = float(sys.argv[11])

  # Get eventList
  eventList = None
  try:
    f=h5py.File(eventH5File,"r")
    eventList = f['likeli'][:nTopEvents,0]
  except Exception as e:
    print "Error:", e
    print "Exit the program"
    exit()
  print 'Found %d events'%(len(eventList))
  
  # Initialize 
  pFOMan = peakFindingOptimizerMan(exp, runNo, eventList, target=targetFile, mask=maskFile, qName=qName, nProc=nProc)
  pFOMan.optimize(detz_offset=detz_offset, window_size=window_size, step_size=step_size)
