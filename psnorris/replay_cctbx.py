from cctbxPlay import cctbxPlayMan
import time

def timeout(cPMan, playActivity):
  while True:
    results = cPMan.isDone(playActivity=playActivity)
    print results
    if results[0]:  
      break
    else:
      time.sleep(5)
  
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
  
