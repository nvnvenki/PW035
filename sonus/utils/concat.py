import fnmatch
import getopt
import os
import sys
import subprocess

cmd = "ffmpeg -i args -acodec copy {0}.mp3"

def concat(dirpath=os.getcwd(), formats="mp3:ogg:wav", separator=":"):
    os.chdir(dirpath)
    all_files = os.listdir(dirpath)

    songs = list()

    formats = formats.split(separator)

    for format in formats:
        songs.extend(fnmatch.filter(all_files, '*.' + format))

    arg = reduce(lambda x, y: x + '|' + y, songs)

    command = cmd.format(os.path.split(os.getcwd())[-1]).split(" ")

    command[2] = 'concat:' + arg

    subprocess.call(command)

if __name__ == '__main__':
    dirpath = os.getcwd()

    formats = "mp3:ogg:wav"

    separator = ":"

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:f:s:',
                                   ['dirpath=', 'formats=', 'separator='])

        for option, argument in opts:
            if option in ('-d', '--dirpath'):
                dirpath = argument
            elif option in ('-f', '--formats'):
                formats = argument
            elif option in ('-s', '--separator'):
                separator = argument
            else:
                print 'invalid option'
                sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)

    concat(dirpath=dirpath, formats=formats, separator=separator)