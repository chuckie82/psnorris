import numpy as np
import h5py

class Stream:
    def label_stream(self, fstream):
        label_id = {0:'----- Begin chunk -----', 
                    1:'Image filename:',
                    2:'Event: //',
                    3:'Peaks from peak search',
                    4:'End of peak list',
                    5:'--- Begin crystal',
                    6:'Reflections measured after indexing',
                    7:'End of reflections',
                    8:'--- End crystal',
                    9:'----- End chunk -----'}
        level = [1,1,1,1,1,2,2,2,2,1]

        f = open(fstream, 'r')
        content = f.readlines()
        f.close()
        
        tmpLabel = [[] for i in range(len(label_id))]
        for i, val in enumerate(content):
            for j in range(len(label_id)):
                if label_id[j] in val:
                    tmpLabel[j].append(i)
                    continue

        maxidx = np.argsort(np.array(level))[-1]
        minidx = np.argsort(np.array(level))[0]
        maxcol = len( tmpLabel[maxidx] )

        FinLabel = (-10)*np.ones((maxcol, len(label_id))).astype(int)
        for i in range(maxcol):
            FinLabel[i, maxidx] = tmpLabel[maxidx][i]
            for j in range(0, maxidx):
                index = np.where( np.array(tmpLabel[j]) < tmpLabel[maxidx][i])[0]
                FinLabel[i, j] = tmpLabel[j][index[-1] ]
            for j in range(maxidx+1, len(label_id)):
                index = np.where( np.array(tmpLabel[j]) > tmpLabel[maxidx][i])[0]
                FinLabel[i, j] = tmpLabel[j][ index[0] ]
        mincol = len(np.unique(FinLabel[:, minidx]))
        print '### indexed patterns: ', mincol
        print '### indexed crystals: ', maxcol
        return FinLabel

    def get_eventList(self, fcxi):
        try: 
            f = h5py.File(fcxi, 'r')
            ievent = f['LCLS/eventNumber'].value
            f.close()
            return  ievent
        except: raise Exception('no such file: '+fcxi)
            
    def get_real_peak(self, fstream, ilabel=None):
        if ilabel is None: 
            ilabel = self.label_stream(fstream)
            ilabel = ilabel[3:5].copy()
        f = open(fstream, 'r')
        content = f.readlines()
        f.close()
        maxNpeak = int(np.amax(ilabel[:,1]-ilabel[:,0]-2))
        
        irealPeak = np.zeros((maxNpeak, 3, len(ilabel)))
        for i in range( len(ilabel) ):
            peakList = content[(ilabel[i,0]+2): ilabel[i,1]]
            for j in range(ilabel[i,1]-ilabel[i,0]-2):
                val = peakList[j].split()
                irealPeak[j,0,i] = float(val[0])
                irealPeak[j,1,i] = float(val[1])
                irealPeak[j,2,i] = float(val[3])
        return irealPeak
        
    def get_pred_peak(self, fstream, ilabel=None):
        if ilabel is None: 
            ilabel = self.label_stream(fstream)
            ilabel = ilabel[6:8].copy()
        f = open(fstream, 'r')
        content = f.readlines()
        f.close()
        maxNpeak = int(np.amax(ilabel[:,1]-ilabel[:,0]-2))
        
        ipredPeak = np.zeros((maxNpeak, 7, len(ilabel)))
        for i in range( len(ilabel) ):
            peakList = content[(ilabel[i,0]+2): ilabel[i,1]]
            for j in range(ilabel[i,1]-ilabel[i,0]-2):
                val = peakList[j].split()
                ipredPeak[j,0,i] = float(val[0])
                ipredPeak[j,1,i] = float(val[1])
                ipredPeak[j,2,i] = float(val[2])
                ipredPeak[j,3,i] = float(val[3])
                ipredPeak[j,4,i] = float(val[4])
                ipredPeak[j,5,i] = float(val[7])
                ipredPeak[j,6,i] = float(val[8])
        return ipredPeak
    
    
    def extract_stream(self, fstream, label=None):
        
        if label is None: label = self.label_stream(fstream)
        f = open(fstream, 'r')
        content = f.readlines()
        f.close()
        data = np.ones((len(label), 23))*(-10)

        for i in range(len(data)):
            val = content[label[i, 1]]
            data[i, 0] = int(val.split('/')[-2].split('r')[1])
            fcxi = val.split(':')[1].lstrip().rstrip()
            
            val = content[label[i, 2]]
            data[i, 2] = int(val.split('//')[-1])
            
            for j in range(label[i, 2], label[i, 3]):
                val = content[j]
                if 'num_peaks =' in val:
                    if data[i,3]<-9: data[i,3] = int(val.split('=')[-1])
                    else: raise Exception('error ... ')

            for j in range(label[i,5], label[i,6]):
                val = content[j]
                if 'num_reflections =' in val:
                    data[i, 4] = int(val.split('=')[-1])
                elif 'Cell parameters' in val:
                    cxiEvent = self.get_eventList( fcxi )    
                    data[i, 1] = cxiEvent[ int(data[i,2]) ]
                    data[i, 14] = float(val.split()[2])
                    data[i, 15] = float(val.split()[3])
                    data[i, 16] = float(val.split()[4])
                    data[i, 17] = float(val.split()[6])
                    data[i, 18] = float(val.split()[7])
                    data[i, 19] = float(val.split()[8])
                elif 'astar =' in val:
                    data[i, 5] = float(val.split()[2])
                    data[i, 6] = float(val.split()[3])
                    data[i, 7] = float(val.split()[4])
                elif 'bstar =' in val:
                    data[i, 8] = float(val.split()[2])
                    data[i, 9] = float(val.split()[3])
                    data[i, 10] = float(val.split()[4])
                elif 'cstar =' in val:
                    data[i, 11] = float(val.split()[2])
                    data[i, 12] = float(val.split()[3])
                    data[i, 13] = float(val.split()[4])
                elif 'det_shift' in val:
                    data[i, 20] = float(val.split()[3])
                    data[i, 21] = float(val.split()[6])
        
        realPeak = self.get_real_peak(fstream, label[:,3:5].copy())
        predPeak = self.get_pred_peak(fstream, label[:,6:8].copy())
        
        info = np.around( data[:,0:5].copy() ).astype(int)
        crystal = data[:,5:22].copy()
        print '### finished extraction ...'
        return [label, info, crystal, realPeak, predPeak]
    
    def convert_stream(self, fstream, fsave=None):
        if fsave is None: fsave='stream-extract-data.h5'
        [label, info, crystal, realPeak, predPeak] = self.extract_stream(fstream)
        
        f = h5py.File(fsave, 'w')
        ilabel =    f.create_dataset('label', label.shape, dtype='int')
        iinfo =     f.create_dataset('info', info.shape, dtype='int')
        icrystal =  f.create_dataset('crystal', crystal.shape)
        chunkx = ( realPeak.shape[0], realPeak.shape[1], 1)
        irealPeak = f.create_dataset('realPeak', realPeak.shape, chunks=chunkx, compression='gzip', compression_opts=7)
        chunkx = ( predPeak.shape[0], predPeak.shape[1], 1)
        ipredPeak = f.create_dataset('predPeak', predPeak.shape, chunks=chunkx, compression='gzip', compression_opts=7)
        ilabel[...] = label
        iinfo[...] = info
        icrystal[...] = crystal
        irealPeak[...] = realPeak
        ipredPeak[...] = predPeak
        ilabel.attrs['Column Name'] = '0-Begin_chunk;  1-Image_filename;  2-Event;  3-Peaks;  4-End_of_peak;  \
        5-Begin_crystal;  6-Reflections;  7-End_of_reflections;  8-End_crystal;  9-End_chunk'
        iinfo.attrs['Column Name'] = '0-runNumber;  1-eventNumber;  2-series;  3-nPeaks;  4-numReflection'
        icrystal.attrs['Column Name'] = '0:2-astar;  3:5-bstar;  6:8-cstar;  9:14-lattice;  15:16-xyshift'
        irealPeak.attrs['Column Name'] = '0-fs/px;  1-ss/px;  2-intensity'
        ipredPeak.attrs['Column Name'] = '0:2-hkl;  3-intensity;  4-sigma;  5-fs/px;  6-ss/px'
        f.close()

