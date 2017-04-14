from subprocess import call
import sys

def launch_phenix_refine(mtzfile, pdbfile):
  """
  The function takes a merged mtz and pdb files, then run phenix.refine for
  1 cycle and output the refined map for coot.
  """
  call(['phenix.refine', mtzfile, pdbfile, 'main.number_of_macro_cycles=1', \
  'xray_data.r_free_flags.generate=True', 'nproc=16', 'strategy=none'])
  

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
    
