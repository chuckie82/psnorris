from cctbxPlay import cctbxPlayMan
from psana import *
from xfel.cxi.cspad_ana import cspad_tbx
import time, os, glob, warnings, random
import numpy as np
import cPickle as pickle
from subprocess import call
import subprocess
from collections import Counter
from cctbx import miller, crystal
from cctbx.array_family import flex

class symmetryMan:
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


  def getSymmetryParameters(self, *args):
    """
    Get mean unit cell, mean hi-res, merge once (no-postrefine) then run
    pointless to obtain the mostly-likely spacegroup
    """
    # from a given experiment-run-event_list, 
    cPMan = cctbxPlayMan(self.exp, self.runNo, 0, self.target, self.resultFolder, self.qName, self.nProc,
        self.strTs, *args)
    cPMan.buildPlayground(replaceDir=True)
    # Integrate
    cPMan.doIntegrate()
    # only Exit when all jobs are done
    while True:
      isDone, msg, n_integrated = cPMan.isDone(playActivity="doIntegrate")
      if isDone:
        print "Done."
        break
      else:
        print "Waiting..."
        time.sleep(5)
    #get unit-cell, resolution, and space group from these integration results
    n_atleast_integrated = -1
    nMaxIntegrations = 100
    nMaxIntPointless = 5
    if n_integrated > n_atleast_integrated:
      from dxtbx.model.experiment_list import ExperimentListFactory
      intPicklesAll = glob.glob(os.path.join(self.playground,'out','*_integrated.pickle'))
      intPickles = [intPicklesAll[i] for i in random.sample(range(len(intPicklesAll)), nMaxIntegrations)]
      ucList = np.empty((len(intPickles),6))
      ucList[:] = np.NAN
      resList = np.empty(len(intPickles),)
      resList[:] = np.NAN
      spaceGroupSymbols = []
      for i, intPickle in enumerate(intPickles):
        img_filename_only = os.path.basename(intPickle)
        exp_json_file = os.path.join(os.path.dirname(intPickle),img_filename_only.split('_')[0]+'_refined_experiments.json')
        if os.path.isfile(exp_json_file):
          experiments = ExperimentListFactory.from_json_file(exp_json_file)
          dials_crystal = experiments[0].crystal
          uc_params = dials_crystal.get_unit_cell().parameters()
          space_group = dials_crystal.get_space_group().info()
          obsPickle = pickle.load(open(intPickle, 'rb'))
          ucList[i,:] = list(uc_params)
          resList[i] = min(obsPickle['d'])
          #use pointless to collect the most likely spacegroup
          if i >= nMaxIntPointless: continue
          crystal_symmetry = crystal.symmetry(
              unit_cell=uc_params,
              space_group_symbol=str(space_group))
          miller_set_all=miller.set(
              crystal_symmetry=crystal_symmetry,
              indices=obsPickle['miller_index'],
              anomalous_flag=False)
          observations = miller_set_all.array(
              data=obsPickle['intensity.sum.value'],
              sigmas=flex.sqrt(obsPickle['intensity.sum.variance'])).set_observation_type_xray_intensity()
          mtz_dataset_all = observations.as_mtz_dataset(column_root_label="IOBS")
          mtz_out = os.path.join(self.playground,'pointless',img_filename_only.split('_')[0]+'.mtz')
          mtz_dataset_all.mtz_object().write(file_name=mtz_out)
          cmd = 'pointless hklin '+mtz_out
          process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
          out, err = process.communicate()
          print out

      #calculate mean uc  
      with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_uc = np.nanmean(ucList, axis=0)
        median_uc = np.nanmedian(ucList, axis=0)
        std_uc = np.nanstd(ucList, axis=0)
        median_res = np.nanmedian(resList)
      #get most common spacegroup
      mostCommonSpacegroup,nMostCommonSpacegroup = Counter(spaceGroupSymbols).most_common(1)[0]
      print ','.join(map(str, median_uc)), median_res, mostCommonSpacegroup, nMostCommonSpacegroup
      return 1
