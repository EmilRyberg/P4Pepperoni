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

def main():
	myBroker = ALBroker("myBroker",
		"0.0.0.0",
		0,
		PEPPER_IP,
		PEPPER_PORT)


# Speech recognition
class SpeechRecognition:

	def speech_recognition(self):

		tts=ALProxy("ALTextToSpeech")

         #Getting the service for speech recognition
                asr_service = self.service("ALSpeechRecognition")
                asr_service.setLanguage("English")

                # Setting the vocabulary
                vocabulary=["can","you","hear", "me"]
                asr_service.setVocabulary(vocabulary, False)

	

         #Start the speech recognition engine
                asr_service.subscribe("Subscribe_Name")
	        print 'Speech recognition has started'
	        time.sleep(5)
         #some code here to run when sentence is heard
                asr_service.unsubscribe("Subscribe_Name")
	
class TextToSpeech:
	def text_to_speech(self):
         tts=ALProxy("ALTextToSpeech")
         tts.say("I am speaking")


if __name__=="__main__":
	SpeechRecognition(self)