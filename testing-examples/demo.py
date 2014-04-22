import os
import sys
import test_gmm_win
import time
import getopt
import shutil
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import sonus.feature.mfcc as mfcc
import sonus.utils.sonusreader as sonusreader
import sonus.gmm.gmm as gmm

def main():
    dirpath = os.getcwd()

    home = os.path.expanduser('~')

    objpath = os.path.join(home, "Desktop\\gmm-object")

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:o:',
                                   ['dirpath=', "objpath="])

        for option, argument in opts:
            if option in ('-d', '--dirpath'):
                dirpath = argument
            elif option in ('-o', '--objpath'):
                objpath = argument
            else:
                print 'invalid option'
                sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)

    print dirpath

    print objpath

    all_files = test_gmm_win.list_files(['--dirpath=' + dirpath])

    all_files = map(lambda x: os.path.join(dirpath, x), all_files)

    random.shuffle(all_files)

    gmm_obj = gmm.GaussianMixtureModel.loadobject(objpath)

    print gmm_obj.apriori

    kannada = "kannada"
    english = "english"

    kan_dir = os.path.join(dirpath, kannada)
    eng_dir = os.path.join(dirpath, english)

    try:
        os.mkdir(kan_dir)
        os.mkdir(eng_dir)
    except Exception as e:
        pass

    for file in all_files:
        print 'reading ', file, '...'
        audio_data = sonusreader.SonusReader.from_file(file)

        mfcc_data = mfcc.mfcc(audio_data.data, samplerate=audio_data.samplerate)

        class_ = gmm_obj.fit(mfcc_data)

        if class_ == 0:
            shutil.move(file, kan_dir)

        if class_ == 1:
            shutil.move(file, eng_dir)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print str((end_time - start_time) / 60) + ' minutes...'