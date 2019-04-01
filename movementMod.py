# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 22:02:24 2019

@author: galas
"""
import sys
import time
import argparse #Provide variables at runtime, no idea why

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
from naoqi import ALMath
#import naoqi

PEPPER_IP= 0

PEPPER_PORT=0

class MovementClass(ALModule):
   """Module to handle movement, sort of"""
   def __init__(self, name):
       #Runs at the beginning
       ALModule.__init__(self, name) #Connects to AlModule
       
       #Connect to proxy
       self.animation = ALProxy("ALAnimationPlayer")
       self.tts = ALProxy("ALTextToSpeech")
       self.posture = ALProxy("ALPosture")
       
       #self.speakmove = ALProxy("ALSpeakingMovement") TO BE TESTED. Allows robot to talk and move at the same time
      
     #Create services (use of proxy?)
       self.memory = session.service("ALMemory")
       self.speech_recog = session.service("ALSpeechRecognition")
       self.motion_service = session.service("ALMotion")
       
       
       #Subscribe to EngagementZone event for waving
       #global memory
       
       self.subscriber = self.memory.subscriber("PersonEnteredZone1")
       self.subscriber.signal.connect(self.waving_movem)
       # TODO Change measure of EngageMentZone
       
       
       #Subscribe to SpeechRecognition and WordRecognized
       self.speech_recog_sub = self.speech_recog.subscriber("IsRunning")
       self.speech_recog_sub.signal.connect(self.think_movem)
       
       self.word_recog_sub = self.speech_recog.subscriber("WordRecognized")
       self.word_recog_sub.signal.connect(self.think_movem)
       
       
       #Subscribe to Text to Speech
       self.tts_sub = self.tts.subscriber("TextStarted")
       self.tts_sub.signal.connect(self.speakmovem)
       
       
       
       def waving_movem(self, val):
           self.memory.unsubscribe("PersonEnteredZone1")
           val= self.memory.getData("PersonEnteredZone1")
           
           if val > 0 :
               #self.speakmove.setEnabled(true) TO BE TESTED
               self.animation.run("animations/Stand/Gestures/Hey_1")
               self.tts.post.say("Hello!")
               self.subscriber("EngagementZones/PersonEnteredZone1")
               #pass
               """else:
                  pass"""
        
        def think_movem(self, speech, word_num):
            speech = self.speech_recog_sub.getParameter('value')
            word_num = self.word_recog_sub.getParameter('value') #number of words needed to be recognized
            while speech = true:
                self.animation.run("animations/Stand/Gestures/Thinking_1")
                break
            if speech == false and word_num < 3:
                self.animation.run("animations/Stand/Gestures/IDontKnow_1")
                self.tts.say("Sorry, I didnt understand that")
                
                
        def speak_movem(self, pepper_speaking):
            pepper_speaking = self.tts_sub.getParameter('value')
            while pepper_speaking = true:
                self.animation.run(animations/Stand/BodyTalk/BodyTalk_1)
                break
            
        def looking_movem(self):
            
            #Head Rotation (slow)
            names = "HeadYaw"
            angleLists = [60**almath.TO_RAD, -60*almath.TO_RAD]
            times      = [1.0, 5.0]
            isAbsolute = True
            motion_service.angleInterpolation(names, angleLists, times, isAbsolute)
            
            
        def point_stairs:#do for each location
            
            postureSpeed=0.3
            
            self.posture.goToPosture("Stand", postureSpeed)
            time.sleep(0.1)
            #Set parameters and start moving
            
            jointName = "WristYaw"
            jointAngle = -49.3*ALmath.TO_RAD
            fractionMaxSpeed = 0.3
            
            handName = "RHand"
            #for individual movement
            #Open hand
            motion_service.openHand(handName)
            time.sleep(1.0)
            #Twist Wrist
            motion_service.setStiffnesses(jointName,0.1)
            motion_service.setAngles(jointName,jointAngle,fractionMaxSpeed)
            time.sleep(1.0)
            
            #Start Trajectory 
            names      = ["RShoulderPitch", "RShoulderRoll",]
            angleLists = [[40.3*almath.TO_RAD,-0.4*almath.TO_RAD], [14*almath.TO_RAD],]
            times      = [[1.0,  2.0], [ 1.0], ]
            isAbsolute = True
            motion_service.angleInterpolation(names, angleLists, times, isAbsolute)
            

def main():
    """Main function to run, includes Broker"""
    
    myBroker = ALBroker("myBroker",
    0.0.0.0,
    PEPPER_IP,
    PEPPER_PORT)
    
    #Add main controller of modules here
    
if __name__=="__main__":
    main()
