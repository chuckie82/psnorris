import numpy as np
import h5py

def stream2lattice(path_stream, path_write):
    icrystal = []
    f = open(path_stream,'r')
    content = f.readlines()
    f.close()
    for i, val in enumerate(content):
        if (val[:15] == 'Cell parameters'):
            temp = val.split(' ')
            cry_a = float(temp[2])
            cry_b = float(temp[3])
            cry_c = float(temp[4])
            cry_alpha = float(temp[6])
            cry_beta = float(temp[7])
            cry_gamma = float(temp[8])
            icrystal.append([cry_a, cry_b, cry_c, cry_alpha, cry_beta, cry_gamma])

    icrystal = np.array(icrystal)

    f = h5py.File(path_write, 'w')
    data_write = f.create_dataset('lattice', icrystal.shape)
    data_write[...] = icrystal
    f.close()
