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
import random

# Speech recognition
class SpeechRecognition(object):
    session=None

    def __init__(self,session, ip, port, proxy):
        self.session=session

        #Services
        self.tts = session.service("ALTextToSpeech")
        self.asr = session.service("ALSpeechRecognition")
        self.motion_service = session.service("ALMotion")
        self.proxy = proxy
        self.autonomous_life = ALProxy("ALAutonomousLife", ip, port)
        self.beep = ALProxy("ALAudioDevice", ip, port)

        print "INIT AUDIO"
        atexit.register(self.exit_handler)
        self.random_id = None

        #Speech recognition configurations
        self.asr.pause(True)
        self.asr.removeAllContext()
        self.asr.setVisualExpression(True)
        self.asr.setAudioExpression(True)
        self.asr.setLanguage("English")
        self.asr.removeAllContext()
        # Setting the vocabulary from text file
        vocabulary_file = open("vocabulary", "r")
        vocabulary = vocabulary_file.read().split(',')
        success = False
        for i in range(0,2):
            try:
                self.asr.setVocabulary(vocabulary, False)
            except Exception as e:
                print "[ERROR] Can't set vocabulary"
                self.error_beep()
                #print e
                if i < 1:
                    self.autonomous_life.setState("disabled")
                    self.autonomous_life.setState("solitary")
                    #self.asr = None
                    #self.asr = session.service("ALSpeechRecognition")
                    self.asr.pause(True)
                    self.asr.removeAllContext()
                    time.sleep(1)
            else:
                success = True
                break
        if not success:
            print "[FATAL] Couldn't set vocabulary"
            for i in range(3):
                self.beep.playSine(440, 60, 0, 0.1)
                time.sleep(0.1)
            sys.exit(1)

    def listen(self):
        self.asr.pause(False)
        asr_listen=None

        question=None
        location=None

        self.random_id = "speech" + str(random.randint(0,100000))
        #Start the speech recognition engine
        self.asr.subscribe(self.random_id)
        print "[INFO] Speech recognition is running"

        temp = time.time()
        for i in range (20):
            try:
                self.proxy.removeData("WordRecognized")
            except:
                continue
        print "Wordrecognized clear took %s seconds" % time.time()-temp

	    #Loop that breaks when asr_listen is not empty, otherwise it ends after 10 sec
        success = False
        i = 5
        while i > 0:
            time.sleep(2)
            i = i - 1
            try:
                asr_listen = self.proxy.getData("WordRecognized")
            except Exception as e:
                print "[WARNING] Could not read WordRecognized"
            else:
                if asr_listen != None and asr_listen[0] != 'Pepper' and asr_listen[0] != '' and asr_listen[1] > -2.0 and asr_listen != 'hello':
                    success = True
                    try:
                        self.proxy.removeData("WordRecognized") #clear buffer
                    except Exception as e:
                        print "[WARNING] Could not clear WordRecognized"
                    break

        self.asr.unsubscribe(self.random_id)
        self.asr.pause(True)

	    #If else statement that writes question and local to the corrosponding scenario
        if asr_listen != None and asr_listen != 'hello':
            print asr_listen
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
            elif asr_listen[0]=='can i bring' or asr_listen[0] == 'can this go through' or asr_listen[0]=='security' or asr_listen[0]=='can i carry' or asr_listen[0]=='can i keep' or asr_listen[0]=='is this allowed' or asr_listen[0]=='am i allowed' or asr_listen[0]=='is this dangerous' or asr_listen[0]=='can i board the plane':
                question="object_detection"
            elif asr_listen[0]=='who are you' or asr_listen[0] == 'what are you' or asr_listen[0] == 'what can you do':
                question="identification"
            else:
                print "[ERROR] Unknown phrase:" + asr_listen[0]
                self.error_beep()

        print "[INFO] Speech recognition finished"
        return (question, location, success)

    def say(self, text):
        self.tts.say(text)

    def ready_beep(self):
        self.beep.playSine(1000, 40, 0, 0.1)
        time.sleep(0.2)

    def error_beep(self):
        for i in range (2):
            self.beep.playSine(880, 30, 0, 0.1)
            time.sleep(0.2)
            self.beep.playSine(440, 30, 0, 0.1)
            time.sleep(0.2)

    def fatal_beep(self):
        for i in range(4):
            self.beep.playSine(440, 60, 0, 0.1)
            time.sleep(0.2)

    def exit_handler(self):
        self.asr.unsubscribe(self.random_id)
        self.asr.pause(False)
        print "Exited Audio"

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
