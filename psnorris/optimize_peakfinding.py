#driver for cctbx peakFinding optimizer
from peakFindingOptimizer import peakFindingOptimizerMan

if __name__ == '__main__':
  # Get eventList
  # Todo: open /reg/d/psdm/cxi/cxitut13/res/autosfx/xx.h5 for the list of events
  # and select only top 500
  # Get beamXY

  # Initialize 
  pFOMan = peakFindingOptimizerMan('cxic0415', 101, eventList, beamXY, target='target.phil', mask='mask.pickle', nproc=12)
  pFOMan.optimize(min_spot_size=2, max_spot_size=4)
