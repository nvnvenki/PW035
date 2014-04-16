"""
script for breaking a file into chunks of specified lengths

args:

seperator: seperator used in formats

formats: formats of files to be chunked

length: length in minutes of the files

chunksize: chunksize in minutes
"""

import os
import sys
import subprocess
import glob
import time
import getopt

cmd = "ffmpeg -ss {0} -i {1}.mp3 -t {2} {3}.mp3"

def main():
    # seperator used in formats
    seperator = ':'

    # colon seperated formats
    formats = 'mp3:wav:ogg'

    # in minutes
    length = 10

    # in minutes
    chunksize = 2

    path = os.getcwd()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:f:c:l:p:', ['formats=', 'chunksize=', 'length=', 'path='])

        for option, argument in opts:
            if option == '-s':
                seperator = argument
            elif option in ('-f', '--formats'):
                formats = argument
            elif option in ('-c', '--chunksize'):
                chunksize = argument
            elif option in ('-l', '--length'):
                length = argument
            elif option in ('-p', '--path'):
                path = argument
            else:
                print 'invalid option'
                sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)

    os.chdir(path)

    audio_files = list()

    given_formats = formats.split(seperator)

    for ext in given_formats:
        audio_files.extend(glob.glob('*.' + ext))

    base_names = map(lambda x: os.path.splitext(x)[0], audio_files)

    for name in base_names:
        path_ = os.path.join(path, name)

        # create a new directory
        try:
            os.chdir(path_)
        except Exception as e:
            os.mkdir(path_)
            os.chdir(path_)

        for i in range(0, length, chunksize):
            command = cmd.format(time.strftime('%H:%M:%S', time.gmtime(i * 60)), os.path.join(path, name),
                                 time.strftime('%H:%M:%S', time.gmtime(chunksize * 60)),
                                 name + "_" + str(i) + "_" + str(i + chunksize))

            print command
            #subprocess.call(command.split(" "))

if __name__ == '__main__':
    main()