from cctbxPlay import cctbxPlayMan
import time

def timeout(startTime, limitSec, cPMan, playActivity):
  while time.time() - startTime < limitSec:
    results = cPMan.isDone(playActivity=playActivity)
    print results
    if results[0]:  
      break
    else:
      time.sleep(5)
  
if __name__ == '__main__':
  # Limit polling isDone in seconds
  limitSec = 300
  # Initialize cctbxPlayMan
  cPMan = cctbxPlayMan(exp='cxid9114', runNo=96, trialNo=6, targetPhil='target.phil', outputDir='dials', nproc=12)
  # Create folder structure
  cPMan.buildPlayground(replaceDir=False)
  cPMan.doMerge()
  timeout(time.time(), limitSec, cPMan, 'doMerge')
  """
  # Find spots
  cPMan.findSpots()
  timeout(time.time(), limitSec, cPMan, 'findSpots')
  # Index
  cPMan.doIndex()
  timeout(time.time(), limitSec, cPMan, 'doIndex')
  # Integrate
  cPMan.doIntegrate()
  timeout(time.time(), limitSec, cPMan, 'doIntegrate')
  """
  
