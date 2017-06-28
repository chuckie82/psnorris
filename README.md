# psnorris
"Chuck Norris can reconstruct from destroy-then-diffract experiments"

automation package for LCLS

Setting up the environment:
source ~monarin/cida

Test run cctbx automatic pipeline:
1. Download resource files in test/data to your directory
2. Update format.invalid_pixel_mask in target.phil to your saved mask.pickle
3. In the directory where the resource files are, run python replay_cctbx.py
