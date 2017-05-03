from subprocess import call
import sys, os

class cctbxPlayMan:
  def __init__(self, exp=None, runNo=None, trialNo=None, targetPhil=None, outputDir=None, qName='psanaq', nproc=12):
    self.prog = "Cctbx.xfel wrapper for autosfx"
    self.exp = exp
    self.runNo = runNo
    self.trialNo = trialNo
    self.targetPhil = targetPhil
    self.outputDir = outputDir
    self.qName = qName
    self.nproc = nproc
    self.playground = os.path.join(self.outputDir, 'r{:04d}'.format(self.runNo), '{:03d}'.format(self.trialNo))
    if exp is None or runNo is None or trialNo is None or targetPhil is None:
      print "Please provide experiment name, run no., and target. Exit. Good Bye."
      return 0
      
  def buildPlayground(self, replaceDir=False):
    """
    Create folders for the experiment and run.
    """
    if replaceDir: 
      cmd = ['rm', '-rf', self.playground]
      call(cmd)
      print "Removing", self.playground
    print "Creating", self.playground
    call(['mkdir','-p', os.path.join(self.playground,'out')])
    call(['mkdir','-p', os.path.join(self.playground,'stdout')])
    return 1
        
  
  def findSpots(self):
    """
    Given all the parameters and playground created, run spotfinding using bsub.
    """
    q_cmd = 'mpirun cctbx.xfel.xtc_process input.experiment='+self.exp+' input.run_num='+str(self.runNo)
    q_cmd += ' output.logging_dir='+os.path.join(self.playground,'stdout')+' output.output_dir='+os.path.join(self.playground,'out')
    q_cmd += ' '+self.targetPhil
    cmd = ['bsub', '-n', str(self.nproc), '-q', self.qName, '-o', os.path.join(self.playground,'stdout/log.out'), q_cmd]
    call(cmd)
    return 1
    
  def isDone(self):
    """
    From a stateless bsub job launched in any of the functions here, 
    look for log file and see if it's done.
    """
    qFlag = None
    with open(os.path.join(self.playground,'stdout','log.out'), 'r') as f:
      from cctbxTools import tail
      qFlag = tail(f)[3].strip()
      
    print qFlag=='Successfully completed.'
      
      
    
    
    
    
    
    
