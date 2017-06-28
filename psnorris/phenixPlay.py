import subprocess
import sys, os

class phenixPlayMan:
  def launch_phaser(self, mtzfile, pdbfile, *args):
    """
    The function takes an mtzfile and the model (pdbfile) with
    corresponding phaser parameters (automatically constructed) 
    and performs MR then output PHASER.1.mtz and PHASER.1.pdb
    on the current directory. 
    
    See /reg/common/package/phenix/phenix-1.10.1-2155/modules/phaser/phaser/phenix_interface/__init__.params
    for acceptable keywords.
    """
    subprocess.call(['phenix.phaser', 'phaser.hklin='+mtzfile, 'phaser.model='+pdbfile] + list(args))

  def launch_phenix_refine(self, mtzfile, pdbfile, *args):
    """
    The function takes an mtz and pdb files (e.g. PHASER.1.mtz and PHASER.1.pdb), 
    then runs phenix.refine and outputs the refined map for coot.
    """
    subprocess.call(['phenix.refine', '--overwrite', mtzfile, pdbfile] + list(args))
    

  def launch_coot(self, mtzfile, pdbfile):
    """
    The function takes a refined mtz and pdb files from phenix.refine, then
    call coot to show map.
    """
    subprocess.Popen(['coot','--auto',mtzfile,'--pdb',pdbfile])
    
  

