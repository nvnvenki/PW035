import os
import sys
import test_gmm_win
import time
import test_real_data
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import sonus.feature.mfcc as mfcc
import sonus.utils.sonusreader as sonusreader
import sonus.gmm.gmm as gmm


def main():
    home = os.path.expanduser('~')

    kannada = os.path.join(home, "Desktop\\split_files\\kannada")
    english = os.path.join(home, "Desktop\\split_files\\english")
    hindi = os.path.join(home, "Desktop\\split_files\\hindi")

    kan_files = sorted(test_gmm_win.list_files(['--dirpath=' + kannada]), cmp = test_real_data.comp)
    english_files = sorted(test_gmm_win.list_files(['--dirpath=' + english]), cmp=test_real_data.comp)
    hin_files = sorted(test_gmm_win.list_files(['--dirpath=' + hindi]), cmp = test_real_data.comp)

    nobj = gmm.GaussianMixtureModel.loadobject(os.path.join(home, "Desktop\\split_files\\0.05\\gmm-object"))

    num_files = min(len(english_files), len(kan_files), len(hin_files))

    start = int(num_files * 0.2)

    print start, num_files

    kan_detected = 0
    eng_detected = 0
    hin_detected = 0

    for i in range(start, start + 50):
        print 'reading: ', kan_files[i]
        a = sonusreader.SonusReader.from_file(os.path.join(kannada, kan_files[i]))

        print 'reading: ', english_files[i]

        b = sonusreader.SonusReader.from_file(os.path.join(english, english_files[i]))

        print 'reading: ', hin_files[i]

        c = sonusreader.SonusReader.from_file(os.path.join(hindi, hin_files[i]))

        adata = mfcc.mfcc(a.data, samplerate=a.samplerate)

        bdata = mfcc.mfcc(b.data, samplerate=b.samplerate)

        cdata = mfcc.mfcc(c.data, samplerate=c.samplerate)

        k = nobj.fit(adata)
        e = nobj.fit(bdata)
        h = nobj.fit(cdata)

        #print 'detected ', kan_files[i], ' as', k

        #print 'detected ', english_files[i], ' as', e

        #print 'detected ', hin_files[i], 'as', h

        if k == 1:
            kan_detected += 1
        if e == 0:
            eng_detected += 1
        if h == 2:
            hin_detected += 1

    print '-' * 40
    print 'language\t', 'real\t', 'detected'
    print '-' * 40
    print 'kannada \t', 50, '\t', kan_detected
    print 'english \t', 50, '\t', eng_detected
    print 'hindi   \t', 50, '\t', hin_detected
    print '-' * 40
if __name__ == '__main__':
    s = time.time()
    main()
    print 'elapsed ' + str((time.time() - s) / 60) + 'minutes'