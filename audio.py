import qi
import argparse
import sys
import time
import numpy as np
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import atexit
import inspect

PEPPER_IP="pepper.local"
PEPPER_PORT=9559

# Speech recognition
class SpeechRecognition(object):
    session=None

    def __init__(self,session):
        self.session=session

        #Services
        #self.memory = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        self.asr = session.service("ALSpeechRecognition")
        self.motion_service = session.service("ALMotion")
        self.proxy = ALProxy("ALMemory", PEPPER_IP, PEPPER_PORT)
        self.auto_move = session.service("ALAutonomousLife")
        
        #for subscriber, period, prec in self.asr.getSubscribersInfo():
            #self.asr.unsubscribe(subscriber)

        print "INIT AUDIO"
        #self.tts.setLanguage("Chinese")
        #self.tts.say("hello")
        #self.tts.setLanguage("English")
        #self.tts.say("hello")


        #Subscribing to event
        #self.proxy.subscribeToEvent('WordRecognized', PEPPER_IP, 'wordRecognized')
        atexit.register(self.exit_handler)

        #Speech recognition configurations
        self.asr.pause(True)
        self.asr.removeAllContext()
        #self.asr.pushContexts()
        self.asr.setVisualExpression(True)
        self.asr.setAudioExpression(True)
        self.asr.setLanguage("English")

        # Setting the vocabulary from text file
        vocabulary_file = open("vocabulary", "r")
        vocabulary = vocabulary_file.read().split(',')
        success = False
        for i in range(0,10):
            try:
                self.asr.setVocabulary(vocabulary, False)
            except Exception as e:
                print "[ERROR] Can't set vocabulary"
                self.auto_move.setAutonomousAbilityEnabled("All", False)
                self.motion_service.rest()
                self.motion_service.wakeUp()
                self.auto_move.setAutonomousAbilityEnabled("All", True)
                time.sleep(0.2)
                self.asr = None
                self.asr = session.service("ALSpeechRecognition")
                self.asr.pause(True)
                self.asr.removeAllContext()
                time.sleep(0.2)
            else:
                success = True
                break
        if not success:
            print "[FATAL] Couldn't set vocabulary"
            sys.exit()

        #self.asr.pause(False)

    def __del__(self):
        #self.proxy.unsubscribeToEvent("WordRecognized", "wordRecognized")
        print "unsubscribed from wordsrecognized"

    def listen(self):
        self.asr.pause(False)
        asr_listen=''

        question=None
        location=None

        #Start the speech recognition engine
        self.asr.subscribe("Speech_Question")
        print("Speech recog is running")
	
	    #Loop that breaks when asr_listen is not empty, otherwise it ends after 10 sec
        success = False
        i = 5
        while i > 0:
            time.sleep(2)
            i = i - 1
            asr_listen = self.proxy.getData("WordRecognized")
            if asr_listen != '' and asr_listen[0] != 'Pepper' and asr_listen[0] != '' and asr_listen[1] > -2.0:
                success = True
                self.proxy.removeData("WordRecognized") #clear buffer
                break

        self.asr.unsubscribe("Speech_Question") 

	    #If else statement that writes question and local to the corrosponding scenario
        print("Data: %s" % asr_listen)

        if asr_listen[0] == 'the stairs':
            question="localisation"
            location="stairs"
        elif asr_listen[0] == 'the bathroom' or asr_listen[0] == 'the toilet' or asr_listen[0] == 'the lavatory' or asr_listen[0] == 'the restroom':
            question="localisation"
            location="toilets"
        elif asr_listen[0]=='the canteen' or asr_listen[0] == 'can i get food':
            question="localisation"
            location="canteen"
        elif asr_listen[0]=='the elevator' or asr_listen[0] == 'the lift':
            question="localisation"
            location="elevator"
        elif asr_listen[0]=='the exit' or asr_listen[0] == 'can i leave' or asr_listen[0] == 'can i get out' or asr_listen[0] == 'can i get outside':
            question="localisation"
            location="exit"
        elif asr_listen[0]=='through security' or asr_listen[0] == 'is this dangerous':
            question="object_detection"

        self.asr.pause(True)
        #self.asr.removeAllContext()
        #self.asr.pause(False)

        print "AUDIO LISTEN FINISHED"
        return (question, location, success)
        
    def say(self, text):
        self.tts.say(text)

    def exit_handler(self):     
        #self.asr.pause(False)
        #self.asr.unsubscribe("Speech_Question")
        #self.proxy.unsubscribeToEvent("WordRecognized", "wordRecognized")
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
