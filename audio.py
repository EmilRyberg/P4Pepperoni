import qi
import argparse
import sys
import time
import numpy as np
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import atexit

PEPPER_IP="192.168.43.214"
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
        
        #Subscribing to event
        self.proxy.subscribeToEvent('WordRecognized', PEPPER_IP, 'wordRecognized')
        atexit.register(self.exit_handler)

    def __del__(self):
        self.proxy.unsubscribeToEvent("WordRecognized", "wordRecognized")
        self.proxy.removeData("WordRecognized")
        print "unsubscribed from wordsrecognized"

    def listen(self):
        asr_listen=''

        question=None
        location=None

        #Speech recognition configurations
        self.asr.pause(True)
        self.asr.removeAllContext()
        self.asr.setVisualExpression(True)
        self.asr.setAudioExpression(True)
        self.asr.setLanguage("English")

        # Setting the vocabulary from text file
        vocabulary_file = open("vocabulary", "r")
        vocabulary = vocabulary_file.read().split(',')
        self.asr.setVocabulary(vocabulary, False)
        self.asr.pause(False)

        #Start the speech recognition engine
        self.asr.subscribe("Speech_Question")
        print("Speech recog is running")
	
	    #Loop that breaks when asr_listen is not empty, otherwise it ends after 10 sec
        success = False
        i=5
        while i>0:
            time.sleep(3)
            i=i-1
            asr_listen=self.proxy.getData("WordRecognized")
            if asr_listen != '' and asr_listen[0] != 'Pepper':
                success = True
                break

        self.asr.unsubscribe("Speech_Question")
	
	    #If else statement that writes question and local to the corrosponding scenario
        print("Data: %s" % asr_listen)

        if asr_listen[0] == 'where are the stairs':
            question="localisation"
            location="stairs"
        elif asr_listen[0] == 'where is the bathroom':
            question="localisation"
            location="bathroom"
        elif asr_listen[0]=='where is the canteen':
            question="localisation"
            location="canteen"
        elif asr_listen[0]=='where is the elevator':
            question="localisation"
            location="elevator"
        elif asr_listen[0]=='where is the exit':
            question="localisation"
            location="exit"
        elif asr_listen[0]=='can this go through security':
            question="object_detection"

        self.asr.pause(True)
        self.asr.removeAllContext()
        self.asr.pause(False)

        return (question, location, success)
        
    def say(self, text):
        self.tts.say(text)

    def exit_handler(self):     
        #self.asr.pause(False)
        #self.asr.unsubscribe("Speech_Question")
        self.proxy.unsubscribeToEvent("WordRecognized", "wordRecognized")
        print "unsubscribed from wordsrecognized"

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
"""
