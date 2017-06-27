from subprocess import call
import sys

def launch_phaser(mtzfile, pdbfile, **kwargs):
  """
  The function takes an mtzfile and the model (pdbfile) with
  corresponding phaser parameters (automatically constructed) 
  and performs MR then output PHASER.1.mtz and PHASER.1.pdb
  on the current directory. 
  
  See /reg/common/package/phenix/phenix-1.10.1-2155/modules/phaser/phaser/phenix_interface/__init__.params
  for acceptable keywords.
  """
  params = [str(key)+'='+str(val) for key, val in kwargs.iteritems()]
  tmp = ['phenix.phaser', 'phaser.hklin='+mtzfile, 'phaser.model='+pdbfile] + params
  print tmp
  #call(['phenix.phaser', 'phaser.hklin='+mtzfile, 'phaser.model='+pdbfile])

def launch_phenix_refine(mtzfile, pdbfile):
  """
  The function takes an mtz and pdb files (e.g. PHASER.1.mtz and PHASER.1.pdb), 
  then runs phenix.refine and outputs the refined map for coot.
  """
  #call(['phenix.refine', mtzfile, pdbfile, 'main.number_of_macro_cycles=1', \
  #'xray_data.r_free_flags.generate=True', 'nproc=12', 'strategy=none'])
  
  call(['phenix.refine', '--overwrite', mtzfile, pdbfile, 'xray_data.r_free_flags.generate=True', 'nproc=12'])
  

def lanch_coot(mtzfile, pdbfile):
  """
  The function takes a refined mtz and pdb files from phenix.refine, then
  call coot to show map.
  """
  call(['coot','--auto',mtzfile,'--pdb',pdbfile])
  

if __name__ == "__main__":
  if sys.argv[1:]:
    mtzfile = sys.argv[1]
    pdbfile = sys.argv[2]
    
