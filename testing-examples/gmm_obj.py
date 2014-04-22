import os
import cPickle
import glob
import numpy as np
import h5py
import sys
import test_gmm_win
import time
import getopt
import test_real_data
import multiprocessing as mp

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import sonus.gmm.gmm as gmm

def next(train=0.7):
    path = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files"

    path = os.path.join(path, str(train - 0.1))

    path = os.path.join(path, "MFCC")

    data = np.array([0.] * 39)

    ndir = os.chdir(path)

    files = glob.glob('*')

    files = map(lambda x: os.path.join(path, x), files)

    print files

    print 'reading files for data ', path

    for file in files:
        fobj = open(file, 'rb')
        data = np.vstack((data, cPickle.load(fobj)))
        fobj.close()

    print data.shape

    data = np.delete(data, 0, 0)

    print 'early dim ', data.shape

    print 'train ', train

    kannada = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\kannada"
    english = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\english"
    hindi = "C:\\Users\\Bhuvan Anand\\Desktop\\split_files\\hindi"

    kan_files = sorted(test_gmm_win.list_files(['--dirpath=' + kannada]), cmp=test_real_data.comp)
    english_files = sorted(test_gmm_win.list_files(['--dirpath=' + english]), cmp=test_real_data.comp)
    hindi_files = sorted(test_gmm_win.list_files(['--dirpath=' + hindi]), cmp=test_real_data.comp)

    numfiles = min(len(kan_files), len(english_files), len(hindi_files))

    start = int(round((train - 0.1) * numfiles))
    end = int(round(train * numfiles))

    print 'start ', start
    print 'end ', end

    training_set = []
    for i in range(start, end):
        training_set.extend([os.path.join(kannada, kan_files[i]),
        os.path.join(english, english_files[i]),
        os.path.join(hindi, hindi_files[i])])

    print training_set

    print len(training_set)

    # number of processes
    numprocs = 4

    # create a lock for synchronization
    lock = mp.Lock()

    # create manager for sharing the data
    manager = mp.Manager()

    # create a shared list
    sharedlist = manager.list()

    data1 = np.array([0.] * 39, dtype=np.float32)

    # add the data to shared list
    sharedlist.append(data1)

    chunks = test_real_data.getChunks(training_set, numprocs)

    print chunks
    # processes
    procs = []

    for i in range(numprocs):
        procs.append(mp.Process(target=test_real_data.getMfccs, args=(training_set[chunks[i][0]:chunks[i][1]], sharedlist, lock)))
        procs[-1].start()

    map(lambda x: x.join(), procs)

    # remove first row
    data1 = np.delete(sharedlist[0], 0, 0)

    print 'data 1 dim ', data1.shape

    print 'done computing mfcc'

    # create a memory mapped file
    # filename = os.path.join(mkdtemp(), 'memfile')

    data = np.vstack((data, data1))

    dim = data.shape

    print 'new dim ', dim

    parts = test_real_data.getChunks(data, 5)

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

    a = np.linspace(0.3, 0.5, 3)
    a = a.tolist()

    for i in a:
        next(train=i)

    print str((time.time() - start)/60) + " minutes"