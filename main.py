from common import *
import snowboydecoder_arecord
import speech
import requests
import signal
import serial
import json


interrupted = False
local_tts = False
arduino = serial.Serial('/dev/ttyACM0',9600)


def detectedCallback():
    
    arduino.write('1'.encode())

    try:
        play_audio_file(select(config.get('wav', 'listening')))

        reqText = speech.recognize()
        if (reqText):
            # submit request
            logger.info('Request: {0}'.format(reqText))
            response = requests.post(config.get('core_service', 'url'), json={'text': reqText})

            data = response.json()
            logger.info('Response: {0}'.format(data))
            speech.say(data.get('say'), local_tts)

            media = data.get('play')
            if (media):
                process = play_audio_file_async(media, 0.05)
                logger.debug('Playing media file: {0}'.format(media))
                logger.debug('pid={0}'.format(str(process.pid)))
    except Exception as e:
        logger.exception("message")

    arduino.write('0'.encode())


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

    
if len(sys.argv) == 1:
    logger.info('Error: need to specify ini file')
    logger.info('Usage: python {0} [your ini file]'.format(__file__))
    sys.exit(-1)


# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder_arecord.HotwordDetector(config.get('snowboy', 'model'), sensitivity=[0.8, 0.8], audio_gain=2.0)
logger.info ('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=detectedCallback,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
