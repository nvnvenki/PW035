import fnmatch
import os
from os.path import basename
import subprocess
import getopt
import sys

def converter(dirpath=os.getcwd(), separator=':', formats='mp4:ogv:flv:mkv', outextension='mp3'):
    os.chdir(dirpath)

    all_files = os.listdir(dirpath)

    video_files = list()

    formats = formats.split(separator)

    for format in formats:
        video_files.extend(fnmatch.filter(all_files, '*.' + format))

    video_files = map(lambda x: os.path.join(dirpath, x), video_files)

    command = ['ffmpeg', '-i', '<ifile>', '-ar', '44100', '-vn', '-y', '<ofile>']

    for file in video_files:
        # format the command
        command[2] = file

        command[-1] = os.path.splitext(basename(file))[0] + "." + outextension

        # convert using ffmpeg
        subprocess.call(command)

if __name__ == '__main__':
    dirpath = os.getcwd()

    separator = ':'

    formats = 'mp4:ogv:flv:mkv'

    outextension = 'mp3'

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:s:f:o:',
                                   ['dirpath=', 'separator=', 'formats=', 'outextension='])

        for option, argument in opts:
            if option in ('-s', '--separator'):
                separator = argument
            elif option in ('-f', '--formats'):
                formats = argument
            elif option in ('-d', '--dirpath'):
                dirpath = argument
            elif option in ('-o', '--outextension'):
                outextension = argument
            else:
                print 'invalid option'
                sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)

    converter(dirpath=dirpath, separator=separator, formats=formats, outextension=outextension)