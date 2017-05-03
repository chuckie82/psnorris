from cctbxPlay import cctbxPlayMan

if __name__ == '__main__':
  cPMan = cctbxPlayMan(exp='cxid9114', runNo=96, trialNo=7, targetPhil='target.phil', outputDir='dials', replaceDir=True, nproc=12)
  cPMan.buildPlayground()
  cPMan.findSpots()
  


