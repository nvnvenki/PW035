import os
import sys
import test_gmm_win
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import sonus.feature.mfcc as mfcc
import sonus.utils.sonusreader as sonusreader
import sonus.gmm.gmm as gmm


def main():
    home = os.path.expanduser('~')

    kannada = os.path.join(home, "Desktop\\split_files\\kannada")
    english = os.path.join(home, "Desktop\\split_files\\english")

    kan_files = test_gmm_win.list_files(['--dirpath=' + kannada])
    english_files = test_gmm_win.list_files(['--dirpath=' + english])

    nobj = gmm.GaussianMixtureModel.loadobject(os.path.join(home, "Desktop\\gmm-object"))

    num_files = min(len(english_files), len(kan_files))

    start = int(num_files * 0.7)

    kan_detected = 0
    eng_detected = 0

    print start, num_files

    for i in range(start, num_files):
        print 'reading: ', kan_files[i]
        a = sonusreader.SonusReader.from_file(os.path.join(kannada, kan_files[i]))

        print 'reading: ', english_files[i]

        b = sonusreader.SonusReader.from_file(os.path.join(english, english_files[i]))

        adata = mfcc.mfcc(a.data, samplerate=a.samplerate)

        bdata = mfcc.mfcc(b.data, samplerate=b.samplerate)

        k = nobj.fit(adata)
        e = nobj.fit(bdata)

        print 'detected ', kan_files[i], ' as', k

        print 'detected ', english_files[i], ' as', e

        if k == 0:
            kan_detected += 1

        if e == 1:
            eng_detected += 1

    print kan_detected, eng_detected


if __name__ == '__main__':
    s = time.time()
    main()
    print 'elapsed ' + str((time.time() - s) / 60) + 'minutes'