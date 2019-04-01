import qi
import argparse
import sys
import time
import numpy as np


from naoqi import ALProxy

tts=ALProxy("ALTextToSpeech", "pepper.local", 9559)

tts.say("I am speaking")
