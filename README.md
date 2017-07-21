# psnorris
"Chuck Norris can reconstruct from destroy-then-diffract experiments"

automation package for LCLS

Setting up the environment:
source ~monarin/cida

Update 2017-7-20

Test run cctbx automatic pipeline:
1. Download resource files in test/data to your directory
2. Update detector and sample parameters in target.phil
3. In the directory where the resource files are, run
   
   python replay_cctbx.py -e cxitut13 -r 10 --trial 0 --target target.phil --pdb 1XYZ.pdb
   
   Use -h to see help message.

Test run cctbx geometry (x,y,z):
1. In the directory where the resource files are, run
   
   python optimize_peakfinding.py -e cxitut13 -r 10 --events selected_events.h5 --target target.phil -d 589 -w 10 -s 0.25. 
   
   This will search for detector-to-home distance with median=589 mm in 10 windows with step size=0.25 mm.

Note: detz_offset is the median value where window_size and step_size indicate search range e.g. 500 10 0.25 will search from [498.75, 499.0, 499.25, 499.5, 499.75, 500.0, 500.25, 500.5, 500.75, 501.0] list.

Resuls are stored in current_dir/optims/runNo/trialNo where trialNo corresponds to index of the search list. The on-screen output shows skew values of the distribution of the unit-cell dimensions and the no. of indexed images.


