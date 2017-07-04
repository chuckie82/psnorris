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
  beamXYNpyFile = sys.argv[5]
  targetFile = sys.argv[6]
  maskFile = sys.argv[7]
  qName = sys.argv[8]
  nProc = int(sys.argv[9])
  detz_offset = int(sys.argv[10])
  window_size = int(sys.argv[11])
  step_size = float(sys.argv[12])

  # Get eventList
  eventList = None
  try:
    f=h5py.File(eventH5File,"r")
    eventList = f['likelihood'][0,:nTopEvents].astype(int)
  except Exception as e:
    print "Error:", e
    print "Exit the program"
    exit()
  print 'Found %d events'%(len(eventList))
  
  # Get beamXY
  beamXY = None
  try:
    beamXY = np.load(beamXYNpyFile)
  except Exception as e:
    print "Error", e
    exit()

  # Initialize 
  pFOMan = peakFindingOptimizerMan(exp, runNo, eventList, beamXY, target=targetFile, mask=maskFile, qName=qName, nProc=nProc)
  pFOMan.optimize(detz_offset=detz_offset, window_size=window_size, step_size=step_size)
