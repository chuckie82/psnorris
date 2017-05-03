from subprocess import call
import sys, os

class cctbxPlayMan:
  def __init__(self, exp=None, runNo=None, trialNo=None, targetPhil=None, outputDir=None, replaceDir=False, qName='psanaq', nproc=12):
    self.prog = "Cctbx.xfel wrapper for autosfx"
    self.exp = exp
    self.runNo = runNo
    self.trialNo = trialNo
    self.targetPhil = targetPhil
    self.outputDir = outputDir
    self.replaceDir = replaceDir
    self.nproc = nproc
    if exp is None or runNo is None or trialNo is None or targetPhil is None:
      print "Please provide experiment name, run no., and target. Exit. Good Bye."
      return 0
      
  def buildPlayground(self):
    """
    Create folders for the experiment and run.
    """
    print "cctbxPlay just did this:"
    self.playground = os.path.join(self.outputDir, 'r{:04d}'.format(self.runNo), '{:03d}'.format(self.trialNo))
    if self.replaceDir: 
      cmd = ['rm', '-rf', self.playground]
      call(cmd)
      print cmd
    cmd = ['cxi.mpi_submit', 'dry_run=True', 'output.output_dir='+self.outputDir, \
        'input.experiment='+str(self.exp), 'input.run_num='+str(self.runNo), 'input.trial='+str(self.trialNo)]
    call(cmd)
    print cmd
    return 1
        
  
  def findSpots(self):
    """
    Given all the parameters and playground created, run spotfinding using bsub.
    """
    q_cmd = '"cctbx.xfel.xtc_process input.experiment='+self.exp+' input.run_num='+str(self.runNo)
    q_cmd += ' output.logging_dir='+os.path.join(self.playground,'stdout')+' output.output_dir='+os.path.join(self.playground,'out')
    q_cmd += ' '+self.targetPhil+'"'
    print "cctbxPlay just did this:"
    print q_cmd
    
