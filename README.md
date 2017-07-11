# psnorris
"Chuck Norris can reconstruct from destroy-then-diffract experiments"

automation package for LCLS

Setting up the environment:
source ~monarin/cida

Test run cctbx automatic pipeline:
1. Download resource files in test/data to your directory
2. Update format.invalid_pixel_mask in target.phil to your saved mask.pickle
3. In the directory where the resource files are, run python /path/to/psnorris/replay_cctbx.py

2017-7-3
Test run cctbx geometry (x,y,z):
1. Download resource test/data to your directory
2. In the directory where the resource files are, run
python /path/to/psnorris/optimize_peakfinding.py exp runNo eventListH5File nMaxEvents targetPhilFile maskPickle qName nProc detz_offset window_size step_size

Note: detz_offset is the median value where window_size and step_size indicate search range e.g. 500 10 0.25 will search from [498.75, 499.0, 499.25, 499.5, 499.75, 500.0, 500.25, 500.5, 500.75, 501.0] list.

Resuls are stored in current_dir/optims/runNo/trialNo where trialNo corresponds to index of the search list.
The histogram script can be used to extract unit-cell parameters from each trial.

