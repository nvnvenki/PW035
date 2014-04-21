import os
import sys
from tempfile import NamedTemporaryFile, TemporaryFile
import subprocess
import wave
import re
import scipy.io.wavfile as wav
import warnings

if sys.version_info >= (3, 0):
    basestring = str

converter = 'ffmpeg'


class SonusReader(object):
    """
    Class used for reading the audio from input file.
    the input file can be both audio or video.
    
    can read all audio and video file formats
    that ffmpeg supports.

    system must have ffmpeg installed if want to read files
    of formats other than wav. otherwise it will raise error(OSError).
    """

    def __init__(self, fileName):
        """
        constructor method
        :param fileName: representing the name of the file to read.
        """
        try:
            warnings.simplefilter('ignore', wav.WavFileWarning)
        finally:
            self.samplerate, self.data = wav.read(fileName)

        super(SonusReader, self).__init__()

    @classmethod
    def from_file(cls, fileName, extension=None):
        """
        params
        :param fileName: representing the name of input file
        :param extension: file extension (*.mp3, *.ogg)

        opens and reads the data from the file.
        returns SonusReader object
        """

        fhandler = open(fileName, 'rb')

        # in case of other file formats
        # create temporary files both for inputs and outputs
        # use subprocess module for conversion between file formats
        # read the data of converted .wav file
        # construct the SonusReader obj and return it 

        if extension == 'wav':
            return cls.from_wav(fileName)

        # input file - making sure that source file in left untouched
        inputFile = NamedTemporaryFile(mode='wb', delete=False)
        inputFile.write(fhandler.read())
        inputFile.flush()


        # output file - for getting converted wav files data
        outputFile = NamedTemporaryFile(mode='w+b', delete=False)

        # command for subprocess.call
        command = [converter,
                   '-y',  # ffmpeg option for overwriting existing file
        ]

        # ffmpeg will automatically detect the file format 
        # and chooses the decoders needed
        if extension:
            command += ['-f',
                        extension
            ]
        else:
            command += ['-f',
                        os.path.splitext(fileName)[1][1:].strip().lower()
            ]

        command += [
            '-i', inputFile.name,  # specifying input file
            '-vn',  # drop any video streams in the file
            '-sn',  # drop any subtitles present in the file
            '-f', 'wav',  # specify the output file format needed
            outputFile.name
        ]

        # flush output file
        outputFile.flush()

        # now use ffmpeg for conversion
        subprocess.call(command, stdout=open(os.devnull), stderr=open(os.devnull))

        # now we have a wav file in outputFile construct SonusReader obj
        obj = cls.from_wav(outputFile.name)

        # now close all temporary files - they will be removed from 
        # file system

        inputFile.close()
        outputFile.close()
        os.unlink(inputFile.name)
        os.unlink(outputFile.name)

        return obj

    @classmethod
    def from_wav(cls, fileName):
        """
        params
        :param fileName: file name to read
        """
        outputFile = NamedTemporaryFile(mode='w+b', delete=False)
        command = [
            converter, '-y',
            '-i', fileName,  # specifying input file
            '-vn',  # drop any video streams in the file
            '-sn',  # drop any subtitles present in the file
            '-f', 'wav',  # specify the output file format needed
            '-ar', '44100',  # uniform sample rate for all audio files
            '-ab', '128k',
            outputFile.name
        ]

        # now use ffmpeg for conversion
        subprocess.call(command, stdout=open(os.devnull), stderr=open(os.devnull))

        outputFile.flush()
        obj = cls(outputFile.name)
        outputFile.close()
        os.unlink(outputFile.name)

        return obj

    @classmethod
    def from_mp3(cls, fileName):
        """
        :param fileName: a mp3 file to read
        """
        return cls.from_file(fileName, extension='mp3')

    @classmethod
    def from_ogg(cls, fileName):
        """
        :param fileName: a ogg file to be read
        """
        return cls.from_file(fileName, extension='ogg')


__all__ = [SonusReader]
