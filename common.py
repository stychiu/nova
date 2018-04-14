import sys
import os
import configparser
import random
import subprocess
import logging

config = configparser.RawConfigParser()
config.read(sys.argv[1])

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger()

def select(_list):
    array = [s.strip() for s in _list.split(',')]
    return array[random.randint(0, len(array) - 1)]


def play_audio_file(fname, volume=0.2):
    """Simple callback function to play a wave file.
    :param str fname: wave file name
    :return: None
    """
    subprocess.call(['play', '-v ' + str(volume), fname], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)


def play_audio_file_async(fname, volume=0.2):
    """Simple callback function to play a wave file.
    :param str fname: wave file name
    :return: None
    """
    return subprocess.Popen(['play', '-v ' + str(volume), fname], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)