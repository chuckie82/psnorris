from cctbxPlay import cctbxPlayMan
from psana import *
from xfel.cxi.cspad_ana import cspad_tbx
import time, os, glob
import numpy as np
import cPickle as pickle
import warnings

class detzOptimizerMan:
  def __init__(self, exp, runNo, eventList, target, resultFolder, qName, nProc):
    self.exp = exp
    self.runNo = runNo
    self.eventList = eventList
    self.target = target
    self.qName = qName
    self.nProc = nProc
    self.resultFolder = resultFolder
    self.strTs = None
    # since cctbx only understand timestamp for event filtering
    # converts eventList to tsList
    if self.exp:
      ds = DataSource('exp='+self.exp+':run='+str(self.runNo)+':idx')
      times = ds.runs().next().times()
      tsList = [cspad_tbx.evt_timestamp((t.seconds(),t.nanoseconds()/1e6)) for i,t in enumerate(times) if i in eventList]
      self.strTs = ' debug.event_timestamp='.join(['']+tsList)
    else:
      print "Experiment not given"
      print "Only creating an empty object"
  
  def optimize(self, detz_offset, window_size, step_size, *args):
    # generate a line search
    windows = range(-int(window_size/2),int(window_size/2))
    detz_offsets = map(lambda x: x*step_size+detz_offset, windows)
    cPManList = []
    for trialCount, detzo in enumerate(detz_offsets):
      # from a given experiment-run-event_list, 
      cPMan = cctbxPlayMan(self.exp, self.runNo, trialCount, self.target, self.resultFolder, self.qName, self.nProc, 
          'format.cbf.detz_offset='+str(detzo), self.strTs, *args)
      cPMan.buildPlayground(replaceDir=True)
      # Index
      cPMan.doIntegrate()
      cPManList.append(cPMan)
    # only Exit when all jobs are done
    while True:
      nTrialDone = 0
      for trialCount, cPMan in enumerate(cPManList):
        results = cPMan.isDone(playActivity="doIntegrate")
        if results[0]: nTrialDone += 1
      if nTrialDone == len(cPManList):
        print "Done. #TrialDone=", nTrialDone
        break 
      else:
        print "Waiting... #TrialDone=", nTrialDone
        time.sleep(5)
    # calculate skewness for unit-cell distributions
    skewList, indexCnList = self.calcUCDistrSkew(cPManList)
    return detz_offsets, skewList, indexCnList
  
  def calcUCDistrSkew(self, cPManList):
    skewList = []
    indexCnList = []
    for trialCount, cPMan in enumerate(cPManList):
      # get a list of integrated pickle
      pickleFileList = glob.glob(os.path.join(cPMan.playground,"out","int*.pickle"))
      indexCnList.append(len(pickleFileList))
      ucList = np.empty((len(pickleFileList),6))
      ucList[:] = np.NAN
      for i, pickleFile in enumerate(pickleFileList):
        try:
          uc_params = pickle.load(open(pickleFile, 'rb'))["observations"][0].unit_cell().parameters()
        except Exception as e:
          continue
        ucList[i,:] = list(uc_params)
      # check /0
      i = 0
      skew = [None]*6
      with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_uc = np.nanmean(ucList, axis=0)
        median_uc = np.nanmedian(ucList, axis=0)
        std_uc = np.nanstd(ucList, axis=0)
      # calculate skew
      for mean, med, std in zip(list(mean_uc), list(median_uc), list(std_uc)):
        if std > 1e-3: skew[i] = 3*(mean-med)/std
        i += 1
      skewList.append(skew)
    return skewList, indexCnList
      
      
