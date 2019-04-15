import Movement
import SpeechRecognition
import VisionModule
import naoqi
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import sys
import time

PEPPER_IP = "192.168.1.15"
PEPPER_PORT = 9559
TIMEOUT = 8

class Controller(object):
    def __init__(self):
        self.movement = Movement()
        self.speech_recognition = SpeechRecognition()
        
        
        
        ALModule.__init__(self)
        self.memory = session.service("ALMemory")
        self.greet_subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone1")
        self.greet_subscriber.signal.connect(self.person_entered_zone)
        
    def person_entered_zone(self):
        self.movement.salute()
        self.wait_for_question()
        
    def wait_for_question(self):
        start = time.time()
        done = False
        timeout = False
        while not done and not timeout:
            self.audio_result = audio.listen()
            if self.audio_result == "nothing":
                self.done = True
            elif time.time()-start > TIMEOUT:
                self.timeout = True          
        if self.done:
            self.respond()
            
    def respond(self):
        if self.audio_result == "localisation":
            result = vision.localise()
            if result != "failed":
                audio.say_voiceline(result)
                movement.point_at(location=result, direction=0)
            else:
                audio.say_voiceline(result)
        elif self.audio_result == "object_detection":
            audio.say_voiceline("object_detection")
            result = vision.classify()
            audio.say_voiceline(result)
            if result == "liquid":
                display.show("liquid_rules")
        self.wait_for_question()
                    

def main():
    controller = Controller()                    
                    
if __name__=="__main__":
    """myBroker = ALBroker("myBroker",
    "0.0.0.0",
    0,
    PEPPER_IP,
    PEPPER_PORT)"""
    session = qi.Session()
    
    try:
        session.connect("tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT))
        #app = qi.Application(["SayHi", "--qi-url=" + "tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT)])
        
    except RuntimeError:
        print("wow")
        sys.exit(1)