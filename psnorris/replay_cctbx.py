from cctbxPlay import cctbxPlayMan
from phenixPlay import phenixPlayMan
import time, glob, shutil, argparse

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
  # Input arguments
  parser = argparse.ArgumentParser(
    description='Run cctbx in batch mode. E.g. python replay_cctbx.py -e cxid9114 -r 100 --trial 0 --target target.phil --pdb 1XYZ.pdb'
  )
  parser.add_argument('-e', '--exp', help='Experiment ID e.g. cxitut13', required=True)
  parser.add_argument('-r', '--run', type=int, help='Run Number', required=True)
  parser.add_argument('-t', '--trial', type=int, help='Trial Number (must be unique)', required=True)
  parser.add_argument('-T', '--target', help='Target file for indexing', required=True)
  parser.add_argument('-o', '--output', default="dials", help='Path to output results')
  parser.add_argument('-q', '--queue', default="psanaq", help='Queuing system that supports bsub')
  parser.add_argument('-n', '--ncpus', default=12, type=int, help='No. of Cores')
  parser.add_argument('-P', '--pdb', help='PDB file', required=True)
  parser.add_argument('-C', '--custom', nargs='*', \
      help='Specify any valid arguments for cctbx.xfel.xtc_process. E.g. --custom format.cbf.invalid_pixel_mask=mask.pickle max_events=100')
  args = parser.parse_args()
  # Initialize cctbxPlayMan
  cPMan = cctbxPlayMan(args.exp, args.run, args.trial, args.target, args.output, args.queue, args.ncpus, *args.custom)
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
  pdbFile = args.pdb
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
 
