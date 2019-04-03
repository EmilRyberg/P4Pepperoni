import qi
import argparse
import sys
import time
import numpy as np
from naoqi import ALProxy

# Speech recognition
class AudioModule

	def speech_recognition(self):

	tts=ALProxy("ALTextToSpeech", "pepper.local", 9559)

	#Getting the service for speech recognition

	asr_service = self.service("ALSpeechRecognition")
	asr_service.setLanguage("English")

	#Setting the vocabulary
	vocabulary=["can","you","hear", "me"]
	asr_service.setVocabulary(vocabulary, False)


	#Start the speech recognition engine
	asr_service.subscribe("Subscribe_Name")
	#some code here to run when sentence is heard
	asr_service.unsubscribe("Subscribe_Name")


	
	def text_to_speech(self)
	tts=ALProxy("ALTextToSpeech", "pepper.local", 9559)

	tts.say("I am speaking")
