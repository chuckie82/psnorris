from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import h5py, json
from mpidata import mpidata
import psana, time
import numpy as np
from PSCalib.GeometryObject import two2x1ToData2x2

def writeStatus(fname,d):
    json.dump(d, open(fname, 'w'))

def convert_peaks_to_cheetah(s, r, c) :
    """Converts seg, row, col assuming (32,185,388)
       to cheetah 2-d table row and col (8*185, 4*388)
    """
    segs, rows, cols = (32,185,388)
    row2d = (int(s)%8) * rows + int(r) # where s%8 is a segment in quad number [0,7]
    col2d = (int(s)/8) * cols + int(c) # where s/8 is a quad number [0,3]
    return row2d, col2d

def getNoe(args):
    runStr = "%04d" % args.run
    ds = psana.DataSource("exp="+args.exp+":run="+runStr+':idx')
    run = ds.runs().next()
    times = run.times()
    # check if the user requested specific number of events
    if args.noe == -1:
        numJobs = len(times)
    else:
        if args.noe <= len(times):
            numJobs = args.noe
        else:
            numJobs = len(times)
    return numJobs

def reshapeHdf5(h5file, dataset, ind, numAppend):
    h5file[dataset].resize((ind + numAppend,))

def cropHdf5(h5file, dataset, ind):
    h5file[dataset].resize((ind,))

def updateHdf5(h5file, dataset, ind, val):
    try:
        h5file[dataset][ind] = val
    except:
        h5file[dataset][ind] = 0

def runmaster(args, nClients):

    runStr = "%04d" % args.run
    fname = args.outDir +"/"+ args.exp +"_"+ runStr + ".cxi"
    grpName = "/entry_1/result_1"
    dset_nPeaks = "/nPeaksAll"
    dset_posX = "/peakXPosRawAll"
    dset_posY = "/peakYPosRawAll"
    dset_atot = "/peakTotalIntensityAll"
    dset_maxRes = "/maxResAll"
    dset_saveTime = "/saveTime"
    dset_calibTime = "/calibTime"
    dset_peakTime = "/peakTime"
    dset_totalTime = "/totalTime"
    dset_rankID = "/rankID"
    statusFname = args.outDir + "/status_peaks.txt"

    powderHits = None
    powderMisses = None

    maxSize = 0
    numInc = 0
    inc = 100
    dataShape = (0,0)
    numProcessed = 0
    numHits = 0
    hitRate = 0.0
    fracDone = 0.0
    numEvents = getNoe(args)
    d = {"numHits": numHits, "hitRate": hitRate, "fracDone": fracDone}
    try:
        writeStatus(statusFname, d)
    except:
        print "Couldn't update status"
        pass

    myHdf5 = h5py.File(fname, 'r+')
    while nClients > 0:
        # Remove client if the run ended
        md = mpidata()
        md.recv()
        if md.small.endrun:
            nClients -= 1
        elif md.small.powder == 1:
            if powderHits is None:
                powderHits = md.powderHits
                powderMisses = md.powderMisses
            else:
                powderHits = np.maximum(powderHits, md.powderHits)
                powderMisses = np.maximum(powderMisses, md.powderMisses)
        else:
            try:
                nPeaks = md.peaks.shape[0]
                maxRes = md.small.maxRes
                if args.profile:
                    calibTime = md.small.calibTime
                    peakTime = md.small.peakTime
                    totalTime = md.small.totalTime
                    rankID = md.small.rankID
            except:
                nPeaks = 0
                maxRes = 0
                continue

            if nPeaks > 2048: # only save upto maxNumPeaks
                md.peaks = md.peaks[:2048]
                nPeaks = md.peaks.shape[0]

            if args.profile: tic = time.time()

            for i,peak in enumerate(md.peaks):
                seg,row,col,npix,amax,atot,rcent,ccent,rsigma,csigma,rmin,rmax,cmin,cmax,bkgd,rms,son = peak[0:17]
                cheetahRow,cheetahCol = convert_peaks_to_cheetah(seg,row,col)
                myHdf5[grpName+dset_posX][md.small.eventNum,i] = cheetahCol
                myHdf5[grpName+dset_posY][md.small.eventNum,i] = cheetahRow
                myHdf5[grpName+dset_atot][md.small.eventNum,i] = atot
                myHdf5.flush()
            myHdf5[grpName+dset_nPeaks][md.small.eventNum] = nPeaks
            myHdf5[grpName+dset_maxRes][md.small.eventNum] = maxRes
            myHdf5.flush()

            if args.profile:
                saveTime = time.time() - tic # Time to save the peaks found per event
                myHdf5[grpName + dset_calibTime][md.small.eventNum] = calibTime
                myHdf5[grpName + dset_peakTime][md.small.eventNum] = peakTime
                myHdf5[grpName + dset_saveTime][md.small.eventNum] = saveTime
                myHdf5[grpName + dset_totalTime][md.small.eventNum] = totalTime
                myHdf5[grpName + dset_rankID][md.small.eventNum] = rankID
                myHdf5.flush()

            # If the event is a hit
            if nPeaks >= args.minPeaks and \
               nPeaks <= args.maxPeaks and \
               maxRes >= args.minRes and \
               hasattr(md, 'data'):
                # Assign a bigger array
                if maxSize == numHits:
                    if args.profile: tic = time.time()
                    reshapeHdf5(myHdf5, '/entry_1/result_1/nPeaks', numHits, inc)
                    myHdf5["/entry_1/result_1/peakXPosRaw"].resize((numHits + inc, 2048))
                    myHdf5["/entry_1/result_1/peakYPosRaw"].resize((numHits + inc, 2048))
                    myHdf5["/entry_1/result_1/peakTotalIntensity"].resize((numHits + inc, 2048))
                    reshapeHdf5(myHdf5, '/entry_1/result_1/maxRes', numHits, inc)
                    reshapeHdf5(myHdf5, '/entry_1/instrument_1/source_1/pulse_width', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/photon_energy_eV', numHits, inc)
                    reshapeHdf5(myHdf5, '/entry_1/instrument_1/source_1/energy', numHits, inc) # J
                    reshapeHdf5(myHdf5, '/entry_1/instrument_1/source_1/pulse_energy', numHits, inc)
                    reshapeHdf5(myHdf5, '/entry_1/instrument_1/detector_1/distance', numHits, inc)
                    reshapeHdf5(myHdf5, '/entry_1/instrument_1/detector_1/x_pixel_size', numHits, inc)
                    reshapeHdf5(myHdf5, '/entry_1/instrument_1/detector_1/y_pixel_size', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/detector_1/EncoderValue', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/detector_1/electronBeamEnergy', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/detector_1/beamRepRate', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/detector_1/particleN_electrons', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/eVernier', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/charge', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/peakCurrentAfterSecondBunchCompressor', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/pulseLength', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/ebeamEnergyLossConvertedToPhoton_mJ', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/calculatedNumberOfPhotons', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/photonBeamEnergy', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/wavelength', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/photon_wavelength_A', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/machineTime', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/machineTimeNanoSeconds', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/fiducial', numHits, inc)
                    reshapeHdf5(myHdf5, '/LCLS/eventNumber', numHits, inc)
                    reshapeHdf5(myHdf5, '/entry_1/experimental_identifier', numHits, inc) # same as /LCLS/eventNumber
                    dataShape = md.data.shape
                    myHdf5["/entry_1/data_1/data"].resize((numHits + inc, md.data.shape[0], md.data.shape[1]))
                    if args.profile:
                        reshapeHdf5(myHdf5, '/entry_1/result_1/reshapeTime', numInc, 1)
                        reshapeTime = time.time() - tic
                        updateHdf5(myHdf5, '/entry_1/result_1/reshapeTime', numInc, reshapeTime)
                    maxSize += inc
                    numInc += 1

                # Save peak information
                updateHdf5(myHdf5, '/entry_1/result_1/nPeaks', numHits, nPeaks)
                myHdf5["/entry_1/result_1/peakXPosRaw"][numHits,:] = myHdf5[grpName+dset_posX][md.small.eventNum,:]
                myHdf5["/entry_1/result_1/peakYPosRaw"][numHits,:] = myHdf5[grpName+dset_posY][md.small.eventNum,:]
                myHdf5["/entry_1/result_1/peakTotalIntensity"][numHits,:] = myHdf5[grpName+dset_atot][md.small.eventNum,:]
                updateHdf5(myHdf5, '/entry_1/result_1/maxRes', numHits, maxRes)
                # Save epics
                updateHdf5(myHdf5, '/entry_1/instrument_1/source_1/pulse_width', numHits, md.small.pulseLength)
                updateHdf5(myHdf5, '/LCLS/photon_energy_eV', numHits, md.small.photonEnergy)
                updateHdf5(myHdf5, '/entry_1/instrument_1/source_1/energy', numHits, md.small.photonEnergy * 1.60218e-19) # J
                updateHdf5(myHdf5, '/entry_1/instrument_1/source_1/pulse_energy', numHits, md.small.pulseEnergy)
                updateHdf5(myHdf5, '/entry_1/instrument_1/detector_1/distance', numHits, md.small.detectorDistance)
                updateHdf5(myHdf5, '/entry_1/instrument_1/detector_1/x_pixel_size', numHits, args.pixelSize)
                updateHdf5(myHdf5, '/entry_1/instrument_1/detector_1/y_pixel_size', numHits, args.pixelSize)
                updateHdf5(myHdf5, '/LCLS/detector_1/EncoderValue', numHits, md.small.lclsDet)
                updateHdf5(myHdf5, '/LCLS/detector_1/electronBeamEnergy', numHits, md.small.ebeamCharge)
                updateHdf5(myHdf5, '/LCLS/detector_1/beamRepRate', numHits, md.small.beamRepRate)
                updateHdf5(myHdf5, '/LCLS/detector_1/particleN_electrons', numHits, md.small.particleN_electrons)
                updateHdf5(myHdf5, '/LCLS/eVernier', numHits, md.small.eVernier)
                updateHdf5(myHdf5, '/LCLS/charge', numHits, md.small.charge)
                updateHdf5(myHdf5, '/LCLS/peakCurrentAfterSecondBunchCompressor', numHits, md.small.peakCurrentAfterSecondBunchCompressor)
                updateHdf5(myHdf5, '/LCLS/pulseLength', numHits, md.small.pulseLength)
                updateHdf5(myHdf5, '/LCLS/ebeamEnergyLossConvertedToPhoton_mJ', numHits, md.small.ebeamEnergyLossConvertedToPhoton_mJ)
                updateHdf5(myHdf5, '/LCLS/calculatedNumberOfPhotons', numHits, md.small.calculatedNumberOfPhotons)
                updateHdf5(myHdf5, '/LCLS/photonBeamEnergy', numHits, md.small.photonBeamEnergy)
                updateHdf5(myHdf5, '/LCLS/wavelength', numHits, md.small.wavelength)
                updateHdf5(myHdf5, '/LCLS/photon_wavelength_A', numHits, md.small.wavelength * 10.)
                updateHdf5(myHdf5, '/LCLS/machineTime', numHits, md.small.sec)
                updateHdf5(myHdf5, '/LCLS/machineTimeNanoSeconds', numHits, md.small.nsec)
                updateHdf5(myHdf5, '/LCLS/fiducial', numHits, md.small.fid)
                updateHdf5(myHdf5, '/LCLS/eventNumber', numHits, md.small.eventNum)
                updateHdf5(myHdf5, '/entry_1/experimental_identifier', numHits, md.small.eventNum) # same as /LCLS/eventNumber
                # Save images
                myHdf5["/entry_1/data_1/data"][numHits, :, :] = md.data
                numHits += 1
                myHdf5.flush()
            numProcessed += 1
            # Update status
            if numProcessed % 120:
                try:
                    hitRate = numHits * 100. / numProcessed
                    fracDone = numProcessed * 100. / numEvents
                    d = {"numHits": numHits, "hitRate": hitRate, "fracDone": fracDone}
                    writeStatus(statusFname, d)
                except:
                    print "Couldn't update status"
                    pass

    # Crop back to the correct size
    cropHdf5(myHdf5, '/entry_1/result_1/nPeaks', numHits)
    myHdf5["/entry_1/result_1/peakXPosRaw"].resize((numHits, 2048))
    myHdf5["/entry_1/result_1/peakYPosRaw"].resize((numHits, 2048))
    myHdf5["/entry_1/result_1/peakTotalIntensity"].resize((numHits, 2048))
    cropHdf5(myHdf5, '/entry_1/result_1/maxRes', numHits)
    cropHdf5(myHdf5, '/entry_1/instrument_1/source_1/pulse_width', numHits)
    cropHdf5(myHdf5, '/LCLS/photon_energy_eV', numHits)
    cropHdf5(myHdf5, '/entry_1/instrument_1/source_1/energy', numHits)
    cropHdf5(myHdf5, '/entry_1/instrument_1/source_1/pulse_energy', numHits)
    cropHdf5(myHdf5, '/entry_1/instrument_1/detector_1/distance', numHits)
    cropHdf5(myHdf5, '/entry_1/instrument_1/detector_1/x_pixel_size', numHits)
    cropHdf5(myHdf5, '/entry_1/instrument_1/detector_1/y_pixel_size', numHits)
    cropHdf5(myHdf5, '/LCLS/detector_1/EncoderValue', numHits)
    cropHdf5(myHdf5, '/LCLS/detector_1/electronBeamEnergy', numHits)
    cropHdf5(myHdf5, '/LCLS/detector_1/beamRepRate', numHits)
    cropHdf5(myHdf5, '/LCLS/detector_1/particleN_electrons', numHits)
    cropHdf5(myHdf5, '/LCLS/eVernier', numHits)
    cropHdf5(myHdf5, '/LCLS/charge', numHits)
    cropHdf5(myHdf5, '/LCLS/peakCurrentAfterSecondBunchCompressor', numHits)
    cropHdf5(myHdf5, '/LCLS/pulseLength', numHits)
    cropHdf5(myHdf5, '/LCLS/ebeamEnergyLossConvertedToPhoton_mJ', numHits)
    cropHdf5(myHdf5, '/LCLS/calculatedNumberOfPhotons', numHits)
    cropHdf5(myHdf5, '/LCLS/photonBeamEnergy', numHits)
    cropHdf5(myHdf5, '/LCLS/wavelength', numHits)
    cropHdf5(myHdf5, '/LCLS/photon_wavelength_A', numHits)
    cropHdf5(myHdf5, '/LCLS/machineTime', numHits)
    cropHdf5(myHdf5, '/LCLS/machineTimeNanoSeconds', numHits)
    cropHdf5(myHdf5, '/LCLS/fiducial', numHits)
    cropHdf5(myHdf5, '/LCLS/eventNumber', numHits)
    cropHdf5(myHdf5, '/entry_1/experimental_identifier', numHits)  # same as /LCLS/eventNumber
    myHdf5["/entry_1/data_1/data"].resize((numHits, dataShape[0], dataShape[1]))
    if args.profile:
        cropHdf5(myHdf5, '/entry_1/result_1/reshapeTime', numInc)

    # Save attributes
    myHdf5["LCLS/detector_1/EncoderValue"].attrs["numEvents"] = numHits
    myHdf5["LCLS/detector_1/electronBeamEnergy"].attrs["numEvents"] = numHits
    myHdf5["LCLS/detector_1/beamRepRate"].attrs["numEvents"] = numHits
    myHdf5["LCLS/detector_1/particleN_electrons"].attrs["numEvents"] = numHits
    myHdf5["LCLS/eVernier"].attrs["numEvents"] = numHits
    myHdf5["LCLS/charge"].attrs["numEvents"] = numHits
    myHdf5["LCLS/peakCurrentAfterSecondBunchCompressor"].attrs["numEvents"] = numHits
    myHdf5["LCLS/pulseLength"].attrs["numEvents"] = numHits
    myHdf5["LCLS/ebeamEnergyLossConvertedToPhoton_mJ"].attrs["numEvents"] = numHits
    myHdf5["LCLS/calculatedNumberOfPhotons"].attrs["numEvents"] = numHits
    myHdf5["LCLS/photonBeamEnergy"].attrs["numEvents"] = numHits
    myHdf5["LCLS/wavelength"].attrs["numEvents"] = numHits
    myHdf5["LCLS/machineTime"].attrs["numEvents"] = numHits
    myHdf5["LCLS/machineTimeNanoSeconds"].attrs["numEvents"] = numHits
    myHdf5["LCLS/fiducial"].attrs["numEvents"] = numHits
    myHdf5["LCLS/photon_energy_eV"].attrs["numEvents"] = numHits
    myHdf5["LCLS/photon_wavelength_A"].attrs["numEvents"] = numHits
    myHdf5["LCLS/eventNumber"].attrs["numEvents"] = numHits
    myHdf5["entry_1/experimental_identifier"].attrs["numEvents"] = numHits
    myHdf5["/entry_1/result_1/nPeaks"].attrs["numEvents"] = numHits
    myHdf5["/entry_1/result_1/peakXPosRaw"].attrs["numEvents"] = numHits
    myHdf5["/entry_1/result_1/peakYPosRaw"].attrs["numEvents"] = numHits
    myHdf5["/entry_1/result_1/peakTotalIntensity"].attrs["numEvents"] = numHits
    myHdf5["/entry_1/result_1/maxRes"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/source_1/energy"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/source_1/pulse_energy"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/source_1/pulse_width"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/detector_1/data"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/detector_1/distance"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/detector_1/x_pixel_size"].attrs["numEvents"] = numHits
    myHdf5["entry_1/instrument_1/detector_1/y_pixel_size"].attrs["numEvents"] = numHits

    if '/status/findPeaks' in myHdf5:
        del myHdf5['/status/findPeaks']
    myHdf5['/status/findPeaks'] = 'success'
    myHdf5.flush()
    myHdf5.close()

    try:
        hitRate = numHits * 100. / numProcessed
        d = {"numHits": numHits, "hitRate": hitRate, "fracDone": 100.}
        writeStatus(statusFname, d)
    except:
        print "Couldn't update status"
        pass

    # Save powder patterns
    fnameHits = args.outDir +"/"+ args.exp +"_"+ runStr + "_maxHits.npy"
    fnameMisses = args.outDir +"/"+ args.exp +"_"+ runStr + "_maxMisses.npy"
    fnameHitsTxt = args.outDir +"/"+ args.exp +"_"+ runStr + "_maxHits.txt"
    fnameMissesTxt = args.outDir +"/"+ args.exp +"_"+ runStr + "_maxMisses.txt"
    fnameHitsNatural = args.outDir +"/"+ args.exp +"_"+ runStr + "_maxHits_natural_shape.npy"
    fnameMissesNatural = args.outDir +"/"+ args.exp +"_"+ runStr + "_maxMisses_natural_shape.npy"

    if powderHits.size == 2 * 185 * 388:  # cspad2x2
        # DAQ shape
        asData2x2 = two2x1ToData2x2(powderHits)
        np.save(fnameHits, asData2x2)
        np.savetxt(fnameHitsTxt, asData2x2.reshape((-1, asData2x2.shape[-1])), fmt='%0.18e')
        # Natural shape
        np.save(fnameHitsNatural, powderHits)
        # DAQ shape
        asData2x2 = two2x1ToData2x2(powderMisses)
        np.save(fnameMisses, asData2x2)
        np.savetxt(fnameMissesTxt, asData2x2.reshape((-1, asData2x2.shape[-1])), fmt='%0.18e')
        # Natural shape
        np.save(fnameMissesNatural, powderMisses)
    else:
        np.save(fnameHits, powderHits)
        np.savetxt(fnameHitsTxt, powderHits.reshape((-1, powderHits.shape[-1])), fmt='%0.18e')
        np.save(fnameMisses, powderMisses)
        np.savetxt(fnameMissesTxt, powderMisses.reshape((-1, powderMisses.shape[-1])), fmt='%0.18e')
