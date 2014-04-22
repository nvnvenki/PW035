import os
import sys
import test_gmm_win
import time
import numpy as np
from tempfile import mkdtemp
import multiprocessing as mp
import cPickle
import h5py
import getopt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import sonus.feature.mfcc as mfcc
import sonus.utils.sonusreader as sonusreader
import sonus.gmm.gmm as gmm

def comp(a, b):
    a = int(a.split('_')[1])
    b = int(b.split('_')[1])

    if a == b:
        return 0
    elif a > b:
        return 1
    else:
        return -1


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

        print 'done processing file: ', filepath

def test(train=0.7):
    print 'train ', train
    kannada = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\kannada"
    english = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\english"
    hindi = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\hindi"

    kan_files = sorted(test_gmm_win.list_files(['--dirpath=' + kannada]), cmp = comp)
    english_files = sorted(test_gmm_win.list_files(['--dirpath=' + english]), cmp=comp)
    hindi_files = sorted(test_gmm_win.list_files(['--dirpath=' + hindi]), cmp=comp)

    numfiles = min(len(kan_files), len(english_files), len(hindi_files))

    len_train_set = int(round(train * numfiles))

    training_set = []
    for i in range(len_train_set):
        training_set.extend([os.path.join(kannada, kan_files[i]),
        os.path.join(english, english_files[i]),
        os.path.join(hindi, hindi_files[i])])

    print 'length train set ', len(training_set)

    # number of processes
    numprocs = 4

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
    # filename = os.path.join(mkdtemp(), 'memfile')

    dim = data.shape

    print 'dimension', dim

    # pickle the data into files

    parts = getChunks(data, 5)

    path = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\" + str(train)

    try:
        os.mkdir(path)
        os.mkdir(os.path.join(path, "MFCC"))
    except Exception as e:
        pass

    for i in range(len(parts)):
        fobj = open(os.path.join(os.path.join(path, "MFCC"), "PART_" + str(i)), "wb")
        cPickle.dump(data[parts[i][0]:parts[i][1]], fobj)
        fobj.close()

    # stored mfcc data into multiple pickled files

    # now store the data into a hdf5 dataset
    hdffile = h5py.File(os.path.join(path, "mfcc_data.hdf5"), "w")

    # now create a dataset
    hdfdataset = hdffile.create_dataset("mfcc_data", shape=dim, dtype=np.float32, data=data)

    # memarrray = np.memmap(filename, dtype=np.float32, mode='w+', shape=dim)

    print 'created memfile map'

    # memarrray[:] = data[:]

    print 'done copying to memfile'

    GMM = gmm.GaussianMixtureModel(hdfdataset, 3, options={
        'method':'kmeans'
        })

    print 'gmm object construction done'

    GMM.expectationMaximization()

    print 'emm done'

    gmm.GaussianMixtureModel.saveobject(GMM, filepath=path)

if __name__ == '__main__':
    start = time.time()
    train = 0.7
    try:
        opts, args = getopt.getopt(sys.argv[1:], 't:',
                                   ['train='])

        for option, argument in opts:
            if option in ('-t', '--train'):
                train = float(argument)
            else:
                print 'invalid option'
                sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)

    test(train)

    print str((time.time() - start)/60) + " minutes"