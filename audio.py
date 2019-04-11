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

dataWord=[]
asr_speech_localization=empty

# Speech recognition
class SpeechRecognition(object):

       def __init__(self):
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

       def speech_recognition(self):

              dataWord=self.proxy.getData("WordRecognized")
              print("Data: %s" % dataWord)

              # Setting the vocabulary
              vocabulary=["can you hear me"]
              self.asr.pause(True)
              self.asr.setVocabulary(vocabulary, False)
              self.asr.pause(False)

              #Start the speech recognition engine
              self.asr.subscribe("Subscribe_Name")
              print("Speech recog is running")
              time.sleep(10)

              self.asr.pause(False)
              self.asr.unsubscribe("Subscribe_Name")

              dataWord=self.proxy.getData("WordRecognized")
              print("Data: %s" % dataWord)
              self.asr.pause(True)
              self.asr.removeAllContext()

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


def main():
       obj=SpeechRecognition()
       obj.speech_localization()
       


if __name__=="__main__":
       session = qi.Session()
       try:
        session.connect("tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT))
        #app = qi.Application(["SayHi", "--qi-url=" + "tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT)])
       except RuntimeError:
        print("wow")
        sys.exit(1)

       main()