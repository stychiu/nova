from common import *
import speech_recognition as sts
import text_to_speech as tts

'''
Use the new_message_callback to interact with the recorded audio after a keyword is spoken.
It uses the speech recognition library in order to convert the recorded audio into text.

Information on installing the speech recognition library can be found at:
https://pypi.python.org/pypi/SpeechRecognition/
'''

r = sts.Recognizer()
mic = sts.Microphone()

def recognize():
    # obtain audio from the microphone
    with mic as source:
        audio = r.listen(source, phrase_time_limit=10)
    play_audio_file(select(config.get('wav', 'processing')))
    
    try:
        # text = r.recognize_google_cloud(audio, credentials_json=config.get('google_cloud_speech', 'credentials_json'))
        # To use PocketSphinx, install the following:
        # sudo apt-get install libpulse-dev
        # pip install pocketsphinx
        text = r.recognize_google(audio)
        return text
    except sts.UnknownValueError:
        logger.info('Speech Recognizer could not understand audio')
    except sts.RequestError as e:
        logger.error('Could not request results from Speech Recognizer; {0}'.format(e))


def say(text, local_tts):
    # if local_tts:
    #     tts.say_pico2wave(text)
    # else:
    #     tts.say_bing_speech(text)
    tts.say_windows(text)