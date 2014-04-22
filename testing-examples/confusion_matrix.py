import sys
import os
import getopt
import time
import test_gmm_win
import test_real_data
import multiprocessing as mp
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import sonus.feature.mfcc as mfcc
import sonus.utils.sonusreader as sonusreader
import sonus.gmm.gmm as gmm

def getCluster(obj, test_set, sharedlist, lock):
    for file in test_set:
        audio = sonusreader.SonusReader.from_file(file)

        mfccdata = mfcc.mfcc(audio.data, samplerate=audio.samplerate)

        lock.acquire()

        sharedlist[-1].append((file, obj.fit(mfccdata)))

        lock.release()

def genConfusionMatrix(obj, test_set):
    # number of processes
    numprocs = 4

    # create a lock for synchronization
    lock = mp.Lock()

    # create manager for sharing the data
    manager = mp.Manager()

    # create a shared list
    sharedlist = manager.list()

    data = list()

    # add the data to shared list
    sharedlist.append(data)

    chunks = test_real_data.getChunks(test_set, numprocs)
    print chunks

    # processes
    procs = []

    for i in range(numprocs):
        procs.append(mp.Process(target=getCluster, args=(obj, test_set[chunks[i][0]:chunks[i][1]], sharedlist, lock)))
        procs[-1].start()

    map(lambda x: x.join(), procs)

    return sharedlist[-1]

if __name__ == '__main__':
    start = time.time()
    train = 0.1
    dirpath = 'C:\\Users\\Bhuvan Anand\\Desktop\\split_files'

    kannada = os.path.join(dirpath, 'kannada')
    english = os.path.join(dirpath, 'english')
    hindi = os.path.join(dirpath, 'hindi')

    # data
    kan_files = sorted(test_gmm_win.list_files(['--dirpath=' + kannada]), cmp=test_real_data.comp)
    english_files = sorted(test_gmm_win.list_files(['--dirpath=' + english]), cmp=test_real_data.comp)
    hindi_files = sorted(test_gmm_win.list_files(['--dirpath=' + hindi]), cmp=test_real_data.comp)

    numfiles = min(len(kan_files), len(english_files), len(hindi_files))

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

    path = os.path.join(dirpath, str(train))

    obj = gmm.GaussianMixtureModel.loadobject(filepath=os.path.join(path, 'gmm-object'))

    test = 10

    start = int(round(train * numfiles))
    print 'start ', start

    end = start + test
    print 'end ', end

    test_set = []
    for i in range(start, end):
        test_set.extend([os.path.join(kannada, kan_files[i]),
        os.path.join(english, english_files[i]),
        os.path.join(hindi, hindi_files[i])])

    print test_set

    print genConfusionMatrix(obj, test_set)

    print str((time.time() - start)/60) + " minutes"