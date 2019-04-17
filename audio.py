import qi
import argparse
import sys
import time
import numpy as np
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

PEPPER_IP="pepper.local"
PEPPER_PORT=9559

# Speech recognition
class SpeechRecognition(object):
    session=None

    def __init__(self,session):
        self.session=session

        #Services
        self.memory = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        self.asr = session.service("ALSpeechRecognition")
        self.proxy = ALProxy("ALMemory", PEPPER_IP, PEPPER_PORT)
        self.auto_move = session.service("ALAutonomousLife")
        
        #Speech recognition setup
        self.asr.pause(True)
        self.asr.setVisualExpression(True)
        self.asr.setAudioExpression(True)
        self.asr.removeAllContext()
        self.proxy.subscribeToEvent('WordRecognized', PEPPER_IP, 'wordRecognized')
        self.asr.setLanguage("English")
        self.asr.pause(False)

    def listen(self):
        #Debugging
        asr_listen=self.proxy.getData("WordRecognized")
        print("Data: %s" % asr_listen)

        asr_listen=''

        question=None
        location=None

        # Setting the vocabulary from text file
        vocabulary_file=open("vocabulary", "r")
        vocabulary=vocabulary_file.read().split(',')
        self.asr.pause(True)
        self.asr.setVocabulary(vocabulary, False)
        self.asr.pause(False)

        #Start the speech recognition engine
        self.asr.subscribe("Speech_Question")
        print("Speech recog is running")
        time.sleep(10)
        self.asr.unsubscribe("Speech_Question")

        asr_listen=self.proxy.getData("WordRecognized")
        print("Data: %s" % asr_listen)

        if asr_listen[0] == 'where are the stairs':
            question="localisation"
            location=0
        elif asr_listen[0] == 'where is the bathroom':
            question="localisation"
            location=1
        elif asr_listen[0]=='where is the canteen':
            question="localisation"
            location=2
        elif asr_listen[0]=='where is the elevator':
            question="localisation"
            location=3
        elif asr_listen[0]=='where is the exit':
            question="localisation"
            location=4
        elif asr_listen[0]=='can this go through security':
            question="object_detection"

        self.asr.pause(True)
        self.asr.removeAllContext()

        return question, location

    """
    def speech_localization(self):

        self.asr.pause(True)
        self.asr.removeAllContext()
        vocabulary_localization=["stairs", "bathroom", "exit", "canteen", "elevator"]
        self.asr.setVocabulary(vocabulary_localization, False)
        self.asr.pause(False)

        self.asr.subscribe("Speech_Localization")
        print("Speechrecog is running")
        time.sleep(5)
        self.asr.unsubscribe("Speech_Localization")
        asr_speech_localization=self.proxy.getData("WordRecognized")
        print("Localization: %s" % asr_speech_localization)

        if asr_speech_localization[0] == 'stairs':
            self.tts.say("Ok, I will find the stairs")

        elif asr_speech_localization[0] == 'bathroom':
            self.tts.say("Ok, I will find the bathroom")

        elif asr_speech_localization[0] == 'exit':
            self.tts.say("Ok, I will find the exit")

        elif asr_speech_localization[0] == 'canteen':
            self.tts.say("Ok, I will find the canteen")

        elif asr_speech_localization[0] == 'elevator':
            self.tts.say("Ok, I will find the elevator")

        else:
            self.tts.say("Sorry, I do not know that location")

        self.asr.pause(True)
        self.asr.removeAllContext()
        
    def speech_object_security(self):

        self.asr.pause(True)
        self.asr.removeAllContext()
        vocabulary_localization=["can i bring this through security", "is this safe", "can i take this through security"]
        self.asr.setVocabulary(vocabulary_localization, False)
        self.asr.pause(False)

        self.asr.subscribe("Speech_Security")
        print("Speechrecog is running")
        time.sleep(5)
        self.asr.unsubscribe("Speech_Security")
        asr_speech_security=self.proxy.getData("WordRecognized")
        print("Localization: %s" % asr_speech_security)

        if asr_speech_localization[0] == 'can i bring this through security':
            self.tts.say("I will check the object")
        elif asr_speech_localization[0] == 'is this safe':
            self.tts.say("I will check the object")
        elif asr_speech_localization[0] == 'can i take this through security':
            self.tts.say("I will check the object")
        else:
            self.tts.say("Sorry, I do not know that location")

        self.asr.pause(True)
        self.asr.removeAllContext()
        """

    def say(self, text):
        self.tts.say(text)

"""
listen() returns the type of question and the location (A function with all the things)

say(text)
"""
def main():
       audio=SpeechRecognition()
       audio.test()

if __name__=="__main__"
       session = qi.Session()
       try:
        session.connect("tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT))
        #app = qi.Application(["SayHi", "--qi-url=" + "tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT)])
       except RuntimeError:
        print("wow")
        sys.exit(1)
    main()
