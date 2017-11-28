import numpy as np
import h5py
import os,sys
import argparse
from Stream import *
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--i', help="input stream file", default='', type=str)
parser.add_argument("-o", '--o', help="output h5 file name", default=None, type=str)
args = parser.parse_args()

fstream = args.i
fsave = args.o
if not os.path.exists(fstream):
    raise Exception('no such stream file ... ')
s = Stream()
s.convert_stream(fstream, fsave)
