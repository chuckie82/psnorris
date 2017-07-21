import h5py
import numpy as np
import matplotlib.pyplot as plt

f = h5py.File('likelihood_output_0002.h5')
data = f['likeli'].value
events = data[:,0]
nPeaks = data[:,1]
likelihood = data[:,2]

print "Top likely events: ", events[:1000]
print "numHits: ", len(np.where(nPeaks>=15)[0])

plt.plot(likelihood,'x')
plt.ylabel('likelihood')
plt.show()
