import glob
import getopt
import os
import sys
import subprocess

cmd = "ffmpeg -i args -acodec copy {0}.mp3"


def concat(dirpath=os.getcwd()):
    os.chdir(dirpath)
    all_files = glob.glob('*.mp3')
    arg = reduce(lambda x, y: x + '|' + y, all_files)
    command = cmd.format(dirpath).split(" ")
    command[2] = 'concat:' + arg
    subprocess.call(command)

if __name__ == '__main__':
    dirpath = os.getcwd()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:',
                                   ['dirpath='])

        for option, argument in opts:
            if option in ('-d', '--dirpath'):
                dirpath = argument
            else:
                print 'invalid option'
                sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)

    concat(dirpath)