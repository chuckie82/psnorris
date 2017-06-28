from cctbxPlay import cctbxPlayMan
from phenixPlay import phenixPlayMan
import time, glob, shutil

def timeout(cPMan, playActivity):
  while True:
    results = cPMan.isDone(playActivity=playActivity)
    print results
    if results[0]:  
      break
    else:
      time.sleep(5)

def getLatestRun(moduleName):
  runList = glob.glob(moduleName+'*')
  if runList:
    latestRun = max([int(runName.split(moduleName)[-1].split('_')[0]) for runName in runList])
  else:
    latestRun = 0
  return latestRun
    
if __name__ == '__main__':
  # Initialize cctbxPlayMan
  cPMan = cctbxPlayMan(exp='cxid9114', runNo=96, trialNo=7, targetPhil='target.phil', outputDir='dials', nproc=72)
  # Create folder structure
  cPMan.buildPlayground(replaceDir=True)
  # Find spots
  cPMan.findSpots()
  timeout(cPMan, 'findSpots')
  # Index
  cPMan.doIndex()
  timeout(cPMan, 'doIndex')
  # Integrate
  cPMan.doIntegrate()
  timeout(cPMan, 'doIntegrate')
  # Merging
  cPMan.doMerge()
  timeout(cPMan, 'doMerge')

  # Now ready to run phenix MR-Refine-Coot
  latestPrimeRun = getLatestRun('Prime_Run_')
  pdbFile = '1dpx_clean.pdb'
  if latestPrimeRun:
    phenixPM = phenixPlayMan()
    # MR by Phaser
    latestPostrefCycle = getLatestRun('Prime_Run_'+str(latestPrimeRun)+'/postref_cycle_')
    phenixPM.launch_phaser('Prime_Run_'+str(latestPrimeRun)+'/postref_cycle_'+str(latestPostrefCycle)+'_merge.mtz', 
        pdbFile, 'phaser.model_rmsd=0.8')
    # Open Coot for monitoring
    shutil.copy('PHASER.1.mtz', 'PHASER.1_refine_001.mtz')
    shutil.copy('PHASER.1.pdb', 'PHASER.1_refine_001.pdb')
    phenixPM.launch_coot('PHASER.1_refine_001.mtz', 'PHASER.1_refine_001.pdb')
    # Phenix.refine
    phenixPM.launch_phenix_refine('PHASER.1.mtz', 'PHASER.1.pdb', 'xray_data.r_free_flags.generate=True', 'nproc=12')
  
