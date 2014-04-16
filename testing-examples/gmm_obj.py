import os
import cPickle
import glob
import numpy as np
import h5py
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import sonus.gmm.gmm as gmm

def main():
    cwd = os.getcwd()

    path = "C:\\Users\\bhuvan\\Desktop\\split_files\\mfcc-data"

    data = np.array([0.] * 39)

    ndir = os.chdir(path)

    files = glob.glob('*')

    files = map(lambda x: os.path.join(path, x), files)

    print 'reading files for data'

    for file in files:
        fobj = open(file, 'rb')
        data = np.vstack((data, cPickle.load(fobj)))
        fobj.close()

    data = np.delete(data, 0, 0)

    dim = data.shape

    print 'dimension, ', dim

    print 'constructed data'

    os.chdir(cwd)

    hdffile = h5py.File("C:\\Users\\bhuvan\\Desktop\\split_files\\mfcc_data.hdf5", "w")

    hdfdataset = hdffile.create_dataset("mfcc_data", shape=dim, dtype=np.float32, data=data)

    print 'done creating hdf5 file'

    GMM = gmm.GaussianMixtureModel(hdfdataset, 2, options={
    'method':'kmeans'
    })

    print 'done creating gmm object'

    GMM.expectationMaximization()

    print 'emm done'

    print 'saving object to file'

    gmm.GaussianMixtureModel.saveobject(GMM, filepath="C:\\Users\\bhuvan\\Desktop")

if __name__ == '__main__':
    main()