# coding=utf-8
from __future__ import print_function
import json
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from gtts import gTTS
import http.client
import urllib.parse
import json
from xml.etree import ElementTree
from common import *
import requests


watson_tts = TextToSpeechV1(
    username=config.get('ibm_watson', 'username'),
    password=config.get('ibm_watson', 'password'))


def say_pico2wave(text):
    lang = 'en-US'
    words = '<pitch level=\'140\'>' + text + ''

    fname = join(dirname(__file__), str(os.getpid()) + '.wav')
    subprocess.call(['pico2wave', '--lang', lang, '-w', fname, words])
    play_audio_file(fname)
    os.remove(fname)


def say_watson(text):
    fname = join(dirname(__file__), str(os.getpid()) + '.wav')
    with open(fname, 'wb+') as audio_file:
        audio_file.write(
            watson_tts.synthesize(text, accept='audio/wav', voice=config.get('ibm_watson', 'voice')).content)
    audio_file.close()
    play_audio_file(fname)
    os.remove(fname)


def say_espeak(text):
    voice = 'mb/mb-en1'

    # To use Mbrola voices (better quality than the default espeak voices) on RPi, follow these steps:
    # Obtain mbrola rpi binary from http://www.tcts.fpms.ac.be/synthesis/mbrola/bin/raspberri_pi/mbrola.tgz
    # Uncompress and copy to /usr/bin/
    # Create the folder /usr/share/mbrola/
    # Get voices from http://www.tcts.fpms.ac.be/synthesis/mbrola/mbrcopybin.html
    # Uncompress, enter the voice folder and move the main file named such as "es1" "mx2" etc, to /usr/share/mbrola/

    fname = join(dirname(__file__), str(os.getpid()) + '.wav')
    subprocess.call(['espeak', '-w', fname, '-v', voice, text])
    play_audio_file(fname)
    os.remove(fname)


def say_gtts(text):
    # Install libsox-fmt-all for MP3
    # sudo apt-get install libsox-fmt-all
    fname = join(dirname(__file__), str(os.getpid()) + '.mp3')
    _gtts = gTTS(text=text, lang='en', slow=False)
    _gtts.save(fname)
    play_audio_file(fname)
    os.remove(fname)


def say_bing_speech(text):
    ###
    #Copyright (c) Microsoft Corporation
    #All rights reserved. 
    #MIT License
    #Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the ""Software""), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    #The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    #THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    ###

    #Note: The way to get api key:
    #Free: https://www.microsoft.com/cognitive-services/en-us/subscriptions?productId=/products/Bing.Speech.Preview
    #Paid: https://portal.azure.com/#create/Microsoft.CognitiveServices/apitype/Bing.Speech/pricingtier/S0
    apiKey = config.get('microsoft_bing_speech', 'api_key')

    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}

    #AccessTokenUri = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken";
    AccessTokenHost = "api.cognitive.microsoft.com"
    path = "/sts/v1.0/issueToken"

    # Connect to server to get the Access Token
    logger.debug("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    logger.debug(str(response.status) + ' ' + response.reason)

    data = response.read()
    conn.close()

    accesstoken = data.decode("UTF-8")
    logger.debug("Access Token: " + accesstoken)

    body = ElementTree.Element('speak', version='1.0')
    body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
    voice = ElementTree.SubElement(body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
    voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Female')
    voice.set('name', config.get('microsoft_bing_speech', 'voice'))
    voice.text = text

    headers = {"Content-type": "application/ssml+xml", 
                "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm", 
                "Authorization": "Bearer " + accesstoken, 
                "X-Search-AppId": "07D3234E49CE426DAA29772419F436CA", 
                "X-Search-ClientID": "1ECFAE91408841A480F00935DC390960", 
                "User-Agent": "TTSForPython"}
                
    #Connect to server to synthesize the wave
    logger.debug("\nConnect to server to synthesize the wave")
    conn = http.client.HTTPSConnection("speech.platform.bing.com")
    conn.request("POST", "/synthesize", ElementTree.tostring(body), headers)
    response = conn.getresponse()
    logger.debug(str(response.status) + ' ' + response.reason)

    data = response.read()
    conn.close()
    logger.debug("The synthesized wave length: %d" %(len(data)))

    fname = join(dirname(__file__), str(os.getpid()) + '.wav')
    with open(fname, 'wb+') as audio_file:
        audio_file.write(data)
    audio_file.close()
    play_audio_file(fname)
    os.remove(fname)


def say_windows(text):
    # Connect to our own local speech-synthesizer
    url = config.get('local_tts', 'url')
    payload = {'text': text}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data = response.content

    fname = join(dirname(__file__), str(os.getpid()) + '.wav')
    with open(fname, 'wb+') as audio_file:
        audio_file.write(data)
    audio_file.close()
    play_audio_file(fname)
    os.remove(fname)
    