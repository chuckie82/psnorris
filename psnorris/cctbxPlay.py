from subprocess import call
import sys, os

class cctbxPlayMan:
  def __init__(self, exp, runNo, trialNo, 
    targetPhil, outputDir, qName, nProc, *args):
    self.prog = "Cctbx.xfel wrapper for autosfx"
    self.exp = exp
    self.runNo = runNo
    self.trialNo = trialNo
    self.targetPhil = targetPhil
    self.outputDir = outputDir
    self.qName = qName
    self.nProc = nProc
    self.playground = os.path.join(self.outputDir, 'r{:04d}'.format(self.runNo), '{:03d}'.format(self.trialNo))
    self.args = args #additional arguments for Dials parameters
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
    qCmd = 'mpirun cctbx.xfel.xtc_process input.experiment='+self.exp+' input.run_num='+str(self.runNo)
    qCmd += ' output.logging_dir='+os.path.join(self.playground,'stdout')+' output.output_dir='+os.path.join(self.playground,'out')
    qCmd += ' dump_strong=True index=False'
    qCmd += ' '+self.targetPhil
    qCmd += ' '+' '.join(self.args)
    cmd = ['bsub', '-n', str(self.nProc), '-q', self.qName, '-o', os.path.join(self.playground,'stdout','log_findSpots.out'), qCmd]
    call(cmd)
    return 1
    
  def isDone(self, playActivity='findSpots'):
    """
    From a stateless bsub job launched in any of the functions here, 
    look for log file and see if it's done.
    """
    counter = 0
    if not os.path.isfile(os.path.join(self.playground,'stdout','log_'+playActivity+'.out')):
      return False, 'Log output is not ready. Waiting...', counter
    qFlag = None
    with open(os.path.join(self.playground,'stdout','log_'+playActivity+'.out'), 'r') as f:
      #get qFlag
      from cctbxTools import tail
      try:
        qFlag = tail(f)[3].strip()
      except IndexError as err:
        print "Warning:", err
        return False, 'Log output is not ready. Waiting...', counter
 
    #get no. of hits
    import glob
    globRegEx = None
    if playActivity=='findSpots':
      globRegEx = 'hit*strong.pickle'
    elif playActivity=='doIndex':
      globRegEx = '*indexed.pickle'
    elif playActivity=='doIntegrate':
      globRegEx = '*integrated.pickle'
    if globRegEx: 
      counter = len(glob.glob(os.path.join(self.playground,'out',globRegEx)))
    else:
      #for merging, open stdout log.out and look for merge cycle no.
      with open(os.path.join(self.playground,'stdout','log_'+playActivity+'.out'), 'r') as f:
        for line in f:
          if line.find('Summary for ') > -1: 
            if line.split('_')[-2].isdigit(): counter = int(line.split('_')[-2])
            
    return qFlag.find('Success') > -1 or qFlag.find('Exit') > -1, \
        qFlag, counter
        
  def doIndex(self):
    """
    Given all the parameters and playground created, run spotfinding using bsub.
    """
    qCmd = 'mpirun cctbx.xfel.xtc_process input.experiment='+self.exp+' input.run_num='+str(self.runNo)
    qCmd += ' output.logging_dir='+os.path.join(self.playground,'stdout')+' output.output_dir='+os.path.join(self.playground,'out')
    qCmd += ' integrate=False'
    qCmd += ' '+self.targetPhil
    qCmd += ' '+' '.join(self.args)
    cmd = ['bsub', '-n', str(self.nProc), '-q', self.qName, '-o', os.path.join(self.playground,'stdout','log_doIndex.out'), qCmd]
    call(cmd)
    return 1
    
  def doIntegrate(self):
    """
    Given all the parameters and playground created, run spotfinding using bsub.
    """
    qCmd = 'mpirun cctbx.xfel.xtc_process input.experiment='+self.exp+' input.run_num='+str(self.runNo)
    qCmd += ' output.logging_dir='+os.path.join(self.playground,'stdout')+' output.output_dir='+os.path.join(self.playground,'out')
    qCmd += ' '+self.targetPhil
    qCmd += ' '+' '.join(self.args)
    cmd = ['bsub', '-n', str(self.nProc), '-q', self.qName, '-o', os.path.join(self.playground,'stdout','log_doIntegrate.out'), qCmd]
    call(cmd)
    return 1
    
  def doMerge(self):
    """
    Merge all the integration results currently available in the playground 
    """
    isDone, msg, n_integrated = self.isDone(playActivity='doIntegrate')
    n_atleast_integrated = -1
    if n_integrated > n_atleast_integrated:
      qCmd = 'prime.run prime.phil data='+os.path.join(self.playground,'out','*_integrated.pickle')
      qCmd += ' n_processors='+str(self.nProc)
      cmd = ['bsub','-n', str(self.nProc),'-q', self.qName, '-o', os.path.join(self.playground, 'stdout','log_doMerge.out'), qCmd]
      call(cmd)
      return 1
    else:
      return 0
    
    
    
  
    
    
      
      
    
    
    
    
    
    
