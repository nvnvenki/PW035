import os
import sys
import test_gmm_win
import numpy as np
from tempfile import mkdtemp
import multiprocessing as mp

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import sonus.feature.mfcc as mfcc
import sonus.utils.sonusreader as sonusreader
import sonus.gmm.gmm as gmm

def getChunks(fileslist, numprocs):
    """ get the chunks to be executed by each process """

    chunk, extra = divmod(len(fileslist), numprocs)
    chunks = [chunk for i in range(numprocs)]

    if extra:
        for i in range(len(chunks)):
            if extra:
                chunks[i] += 1
                extra -= 1
            else:
                break

    start = 0
    end = 0

    # list of tuples representing the start and end indexes
    result = []

    for i in range(numprocs):
        end = end + chunks[i]
        result.append((start, end))
        start = end

    return result

def getMfccs(fileslist, sharedlist, lock):
    for filepath in fileslist:
	print 'accessing file: ', filepath

        audio = sonusreader.SonusReader.from_file(filepath)

        mfccdata = mfcc.mfcc(audio.data, samplerate=audio.samplerate)

        # before assigning to shared list acquire lock
        lock.acquire()

        # append new data
        sharedlist[0] = np.vstack((sharedlist[0], mfccdata))

        # release lock
        lock.release()

def main():
    kannada = "C:\\Users\\bhuvan\\Desktop\\audio\\kannada"
    english = "C:\\Users\\bhuvan\\Desktop\\audio\\english"

    kan_files = test_gmm_win.list_files(['--dirpath=' + kannada])
    english_files = test_gmm_win.list_files(['--dirpath=' + english])

    numfiles = min(len(kan_files), len(english_files))

    len_train_set = int(round(0.6 * numfiles))

    print len_train_set

    training_set = []
    for i in range(len_train_set):
        training_set.extend([os.path.join(kannada, kan_files[i]),
        os.path.join(english, english_files[i])])

    training_set = training_set[0:6]

    # number of processes
    numprocs = 3

    # create a lock for synchronization
    lock = mp.Lock()

    # create manager for sharing the data
    manager = mp.Manager()

    # create a shared list
    sharedlist = manager.list()

    data = np.array([0.] * 39, dtype=np.float32)

    # add the data to shared list
    sharedlist.append(data)

    chunks = getChunks(training_set, numprocs)

    print chunks
    # processes
    procs = []

    for i in range(numprocs):
        procs.append(mp.Process(target=getMfccs, args=(training_set[chunks[i][0]:chunks[i][1]], sharedlist, lock)))
        procs[-1].start()

    map(lambda x: x.join(), procs)

    # remove first row
    data = np.delete(sharedlist[0], 0, 0)

    print 'done computing mfcc'

    # create a memory mapped file
    filename = os.path.join(mkdtemp(), 'memfile')

    memarrray = np.memmap(filename, dtype=np.float32, mode='w+', shape=data.shape)

    print 'created memfile map'

    memarrray[:] = data[:]

    print 'done copying to memfile'

    GMM = gmm.GaussianMixtureModel(memarrray, 2, options={
        'method':'uniform'
        })

    print 'gmm object construction done'

    GMM.expectationMaximization()

    print 'emm done'

    gmm.GaussianMixtureModel.saveobject(GMM, filepath="C:\\Users\\bhuvan\\sonus\\newsdata")

if __name__ == '__main__':
    main()