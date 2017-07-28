import numpy as np
import scipy.spatial.distance as sd
from PSCalib.CalibFileFinder import deploy_calib_file
import psana
import argparse
import matplotlib.pyplot as plt
parser = argparse.ArgumentParser()
parser.add_argument("exprun", help="psana experiment/run string (e.g. exp=xppd7114:run=43)")
parser.add_argument("areaDetName", help="psana area detector name from 'print evt.keys()' (e.g. cspad)")
parser.add_argument("-o", "--outDir", help="output directory", type=str)
parser.add_argument("-v", "--verbose", help="verbose", default=0, type=int)
args = parser.parse_args()

def findDetectorCentre(I, guessRow=None, guessCol=None, range=0):
    """
    :param I: assembled image
    :param guessRow: best guess for centre row position (optional)
    :param guessCol: best guess for centre col position (optional)
    :param range: range of pixels to search either side of the current guess of the centre
    :return:
    """
    range = int(range)
    # Search for optimum column centre
    if guessCol is None:
        startCol = 1 # search everything
        endCol = I.shape[1]
    else:
        startCol = guessCol - range
        if startCol < 1: startCol = 1
        endCol = guessCol + range
        if endCol > I.shape[1]: endCol = I.shape[1]
    searchArray = np.arange(startCol,endCol)
    scoreCol = np.zeros(searchArray.shape)
    for i, centreCol in enumerate(searchArray):
        A,B = getTwoHalves(I,centreCol,axis=0)
        scoreCol[i] = getCorr(A,B)
    centreCol = searchArray[np.argmin(scoreCol)]
    if args.verbose >= 1:
        plt.plot(searchArray, scoreCol,'x-')
        plt.title(str(centreCol))
        plt.show()

    # Search for optimum row centre
    if guessRow is None:
        startRow = 1 # search everything
        endRow = I.shape[0]
    else:
        startRow = guessRow - range
        if startRow < 1: startRow = 1
        endRow = guessRow + range
        if endRow > I.shape[0]: endRow = I.shape[0]
    searchArray = np.arange(startRow,endRow)
    scoreRow = np.zeros(searchArray.shape)
    for i, centreRow in enumerate(searchArray):
        A,B = getTwoHalves(I,centreRow,axis=1)
        scoreRow[i] = getCorr(A,B)
    centreRow = searchArray[np.argmin(scoreRow)]
    if args.verbose >= 1:
        plt.plot(searchArray, scoreRow,'x-')
        plt.title(str(centreRow))
        plt.show()

    return centreCol,centreRow

# Return two equal sized halves of the input image
# If axis is None, halve along the first axis
def getTwoHalves(I,centre,axis=None):
    if axis is None or axis == 0:
        A = I[:centre,:]
        B = np.flipud(I[centre:,:])

        (numRowUpper,_) = A.shape
        (numRowLower,_) = B.shape
        if numRowUpper >= numRowLower:
            numRow = numRowLower
            A = A[-numRow:,:]
        else:
            numRow = numRowUpper
            B = B[-numRow:,:]
    else:
        A = I[:,:centre]
        B = np.fliplr(I[:,centre:])

        (_,numColLeft) = A.shape
        (_,numColRight) = B.shape
        if numColLeft >= numColRight:
            numCol = numColRight
            A = A[:,-numCol:]
        else:
            numCol = numColLeft
            B = B[:,-numCol:]
    return A, B

def getScore(A,B):
    ind = (A>0) & (B>0)
    dist = sd.euclidean(A[ind].ravel(),B[ind].ravel())
    numPix = len(ind[np.where(ind==True)])
    return dist/numPix

def getCorr(A,B):
    ind = (A>0) & (B>0)
    dist = 1 - np.corrcoef(A[ind].ravel(),B[ind].ravel())[0,1]
    return dist

############################

experimentName = args.exprun.split(':')[0].split('=')[-1]
runNumber = int(args.exprun.split('=')[-1])
detInfo = args.areaDetName

ds = psana.DataSource(args.exprun+':idx')
run = ds.runs().next()
det = psana.Detector(detInfo)
times = run.times()
evt = None
counter = 0
while evt is None:
    evt = run.event(times[counter]) # guarantee we have a valid event
    counter += 1
cx, cy   = det.point_indexes(evt, pxy_um=(0, 0))
pixelSize = det.pixel_size(evt)
print "cx,cy: ", cx, cy
powderImg = np.load(args.outDir+'/'+experimentName+'_'+str(runNumber).zfill(4)+"_"+str(args.areaDetName)+'_max_assem.npy')

import time
tic = time.time()
centreRow, centreCol = findDetectorCentre(np.log(abs(powderImg)+1e-10), cx, cy, range=50)
toc = time.time()
print "time: ", toc-tic
print("Current centre along row,centre along column: ", cx, cy)
print("Optimum centre along row,centre along column: ", centreRow, centreCol)
np.save(args.outDir+'/newCenter_'+experimentName+'_'+str(runNumber).zfill(4)+'.npy', np.array([centreRow, centreCol]))

# Calculate detector translation in x and y
dx = pixelSize * (cx - centreRow)  # microns
dy = pixelSize  * (cy - centreCol)  # microns
geo = det.geometry(evt)
if 'cspad' in detInfo.lower() and 'cxi' in experimentName:
    geo.move_geo('CSPAD:V1', 0, dx=dx, dy=dy, dz=0)
elif 'rayonix' in detInfo.lower() and 'mfx' in experimentName:
    top = geo.get_top_geo()
    children = top.get_list_of_children()[0]
    geo.move_geo(children.oname, 0, dx=dx, dy=dy, dz=0)
elif 'rayonix' in detInfo.lower() and 'xpp' in experimentName:
    top = geo.get_top_geo()
    children = top.get_list_of_children()[0]
    geo.move_geo(children.oname, 0, dx=dx, dy=dy, dz=0)
else:
    print "autoDeploy not implemented"
fname = args.outDir + "/" + str(runNumber) + '-end.data'
print "fname: ", fname
geo.save_pars_in_file(fname)
print "#################################################"
print "Deploying psana detector geometry: ", fname
print "#################################################"
cmts = {'exp': experimentName, 'app': 'psocake', 'comment': 'auto recentred geometry'}
calibDir = '/reg/d/psdm/' + experimentName[:3] + '/' + experimentName +  '/calib'
deploy_calib_file(cdir=calibDir, src=str(det.name), type='geometry', run_start=int(runNumber), run_end=None, ifname=fname, dcmts=cmts, pbits=0)



