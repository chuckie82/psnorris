import numpy as np
import h5py
import matplotlib.pyplot as plt

path_write = '/reg/d/psdm/cxi/cxic0415/res/autosfx/indexcrystfel/info/cxic0415_0100_-1_reorganize.h5'
path_read = '/reg/d/psdm/cxi/cxic0415/res/autosfx/indexcrystfel/temp/cxic0415_0100_-1.h5'
f = h5py.File(path_read, 'r')
data00 = np.array(f[f.keys()[0]])
f.close()
data = data00[1:].copy()
print 'Detector Distance = ', data00[0,0]

def filter1(idata):
    V = []
    for i in range(idata.shape[0]):
        alpha = idata[i,3].copy()/180.*np.pi
        beta = idata[i,4].copy()/180.*np.pi
        gamma = idata[i,5].copy()/180.*np.pi
        la = idata[i,0].copy()
        lb = idata[i,1].copy()
        lc = idata[i,2].copy()
        Volume = la*lb*lc*np.sqrt(1+2.*np.cos(alpha)*np.cos(beta)*np.cos(gamma)-np.cos(alpha)**2-np.cos(beta)**2-np.cos(gamma)**2)
        V.append(Volume)
    return V

def lens(ivec):
    return np.sqrt(np.sum(ivec**2))

def optimize(ix, iy):
    while(lens(ix+iy)<lens(ix)):
        ix = ix+iy
    while(lens(ix-iy)<lens(ix)):
        ix = ix-iy
    while(lens(iy+ix)<lens(iy)):
        iy = iy+ix
    while(lens(iy-ix)<lens(iy)):
        iy = iy-ix        
    return [ix, iy]

def ang(ix, iy):
    return np.arccos(np.dot(ix, iy)/lens(ix)/lens(iy))

def lattice2direction(ila, ilb, ilc, ialpha, ibeta, igamma):
    ialpha = ialpha/180.*np.pi
    ibeta = ibeta/180.*np.pi
    igamma = igamma/180.*np.pi
    iva = np.array([1., 0, 0])*ila
    ivb = np.array([np.cos(igamma), np.sin(igamma), 0])*ilb
    ivc = np.array([np.cos(ibeta), (np.cos(ialpha)-np.cos(ibeta)*np.cos(igamma))/np.sin(igamma), np.sqrt(1+2.*np.cos(ialpha)*np.cos(ibeta)*np.cos(igamma)-np.cos(ialpha)**2-np.cos(ibeta)**2-np.cos(igamma)**2)/np.sin(igamma)])*ilc
    return [iva, ivb, ivc]

def filter2(idata):
    num = idata.shape[0]
    lattice = np.zeros(idata.shape)
    for i in range(idata.shape[0]):
        iv = np.zeros(9)
        il = np.zeros(9)
        alpha = idata[i,3].copy()/180.*np.pi
        beta = idata[i,4].copy()/180.*np.pi
        gamma = idata[i,5].copy()/180.*np.pi
        la = idata[i,0].copy()
        lb = idata[i,1].copy()
        lc = idata[i,2].copy()
        va = np.array([1,0,0])*la
        vb = np.array([np.cos(gamma), np.sin(gamma), 0])*lb
        vc = np.array([np.cos(beta), (np.cos(alpha)-np.cos(beta)*np.cos(gamma))/np.sin(gamma), np.sqrt(1+2.*np.cos(alpha)*np.cos(beta)*np.cos(gamma)-np.cos(alpha)**2-np.cos(beta)**2-np.cos(gamma)**2)/np.sin(gamma)])*lc
        
        [va, vb] = optimize(va, vb)
        [va, vc] = optimize(va, vc)
        [vb, vc] = optimize(vb, vc)
            
        Nla = lens(va)
        Nlb = lens(vb)
        Nlc = lens(vc)
        iv = np.array([va, vb, vc]).copy()
        il = np.array([Nla, Nlb, Nlc]).copy()
        iarg = np.argsort(il)
        va = iv[iarg[0]].copy()
        vb = iv[iarg[1]].copy()
        vc = iv[iarg[2]].copy()
        
        if np.dot(np.cross(va, vb), vc) < 0:
            vb = -vb
        
        Nla = il[iarg[0]].copy()
        Nlb = il[iarg[1]].copy()
        Nlc = il[iarg[2]].copy()
        Nalpha = ang(vb, vc)/np.pi*180.
        Nbeta = ang(va, vc)/np.pi*180.
        Ngamma = ang(va, vb)/np.pi*180.
        
        Asum_m = Nalpha + Nbeta + Ngamma
        Asum_a = Nalpha + 180.- Nbeta + 180. - Ngamma
        Asum_b = 180. - Nalpha + Nbeta + 180. - Ngamma
        Asum_c = 180. - Nalpha + 180. - Nbeta + Ngamma
        Amin = Asum_m  #np.amin(np.array((Asum_m, Asum_a, Asum_b, Asum_c)))
        
        #if np.abs(Asum_m - Amin) < 2:
        #    pass
        if Amin - Asum_a > 2: 
            Nbeta = 180. - Nbeta
            Ngamma = 180. - Ngamma
	    Amin = Asum_a
        if Amin - Asum_b > 2:
            Nalpha = 180. - Nalpha
            Ngamma = 180. - Ngamma
	    Amin = Asum_b
        if Amin - Asum_c > 2:
            Nalpha = 180. - Nalpha
            Nbeta = 180. - Nbeta
            
        lattice[i] = [Nla, Nlb, Nlc, Nalpha, Nbeta, Ngamma]
        
    return lattice

def refine(idata, iidx, imin, imax):
    index = np.where(idata[:, iidx] > imin)
    idata = idata[index].copy()
    index = np.where(idata[:, iidx] < imax)
    idata = idata[index].copy()
    return idata

data2 = data.copy()
data3 = data.copy()
num_1 = data.shape[0]
V = filter1(data3)
V = np.array(V)
median = np.median(V)
index = np.where(V>median*0.96)
V = V[index].copy()
data2 = data2[index].copy()
index = np.where(V<median*1.04)
V = V[index].copy()
data2 = data2[index].copy()
num_2 = data2.shape[0]

mean_uc = np.mean(V)
median_uc = np.median(V)
std_uc = np.std(V)
print 'Vmedian = ', median_uc, ' Vmean = ', mean_uc, ' Vstd = ', std_uc
print 'Volume Skew = ', 3*np.abs(mean_uc - median_uc)/std_uc, '\n'

lattice = filter2(data2)
imedian = np.median(lattice, axis=0)
num_3 = lattice.shape[0]
print 'Median = ', np.around(imedian, 3)

lattice = refine(lattice, 0, 0.96*imedian[0], 1.04*imedian[0])
lattice = refine(lattice, 1, 0.96*imedian[1], 1.04*imedian[1])
lattice = refine(lattice, 2, 0.96*imedian[2], 1.04*imedian[2])
lattice = refine(lattice, 3, 0.96*imedian[3], 1.04*imedian[3])
lattice = refine(lattice, 4, 0.96*imedian[4], 1.04*imedian[4])
lattice = refine(lattice, 5, 0.96*imedian[5], 1.04*imedian[5])
num_4 = lattice.shape[0]

imean = np.mean(lattice, axis = 0)
print 'Mean   = ', np.around(imean, 3), '\n'
print 'data size = ', num_1, num_2, num_3, num_4, '\n'

f = h5py.File(path_write, 'w')
data_write = f.create_dataset('lattice', lattice.shape)
data_write[...] = lattice
f.close()

fig, ax = plt.subplots(figsize=[10,10])
plt.subplot(3,2,1)
plt.hist(lattice[:,0], bins=50)
plt.title('a')
plt.subplot(3,2,2)
plt.hist(lattice[:,1], bins=50)
plt.title('b')
plt.subplot(3,2,3)
plt.hist(lattice[:,2], bins=50)
plt.title('c')
plt.subplot(3,2,4)
plt.hist(lattice[:,3], bins=50)
plt.title('alpha')
plt.subplot(3,2,5)
plt.hist(lattice[:,4], bins=50)
plt.title('beta')
plt.subplot(3,2,6)
plt.hist(lattice[:,5], bins=50)
plt.title('gamma')
plt.tight_layout()
plt.show()

