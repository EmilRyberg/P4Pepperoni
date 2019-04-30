from movement import Movement
from audio import SpeechRecognition
from vision import VisionModule
from display import Display
#import naoqi
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import sys
import time
import atexit

PEPPER_IP = "192.168.43.214"
PEPPER_PORT = 9559

LOCALISATION_TRESHOLD = 0.90
DANGEROUS_TRESHOLD = 0.95
NONDANGEROUS_TRESHOLD = 0.95
LIQUID_TRESHOLD = 0.5

CLASSIFY_TIMEOUT = 5
OBJECT_DETECTION_TRIES = 3

class Controller(object):
    def __init__(self):
        session = qi.Session()
        try:
            session.connect("tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT))
            #app = qi.Application(["SayHi", "--qi-url=" + "tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT)])
        except RuntimeError:
            print("session connect failed")
            sys.exit(1)
        
        self.movement = Movement(session)
        self.audio = SpeechRecognition(session)
        self.vision = VisionModule(session)
        self.display = Display(session)
        
        self.audio_question = None
        self.audio_location = None
        self.audio_success = None
        
        self.memory = session.service("ALMemory")
        self.autonomy = session.service("ALAutonomousLife")
        #self.enable_autonomy()
        self.greet_subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone1")
        self.greet_subscriber.signal.connect(self.main_flow)
        self.is_running = False

        atexit.register(self.exit_handler)

        #self.audio_question = "localisation"
        #self.audio_location = "exit"
        #self.respond()
        #self.main_flow()
        
    def main_flow(self, unused=None):
        if (self.is_running):
            print "main is already running"
            return
        self.is_running = True
        print "STARTED MAIN FLOW"
        self.audio_question = None
        self.greet()
        time.sleep(0.5)
        while (self.audio_question == None):
            self.wait_for_question()
        if self.audio_success == False:
            return
        self.respond()
        self.is_running = False
        
    def greet(self):
        #self.movement.salute()
        self.say_voiceline("hello")
        
    def wait_for_question(self):
        self.audio_success = False
        for i in range(0, 3):
            question, location, success = self.audio.listen()
            print "Speech stuff: %s, %s, %s" % (question, location, success)
            if success:
                self.audio_success = True
                self.audio_question = question
                self.audio_location = location
                break
            else:
                self.say_voiceline("audio_failed")
        
    def respond(self):
        if self.audio_question == "localisation":
            print "localising"
            self.say_voiceline("localisation", self.audio_location)
            self.movement.start_movement()
            localisation_success = False
            for i in range(0, 360/15):
                self.movement.turn(15, 600)
                result = self.vision.find_localisation()
                #result = [0,0,0,0,0,0]
                keys = {"canteen":0, "elevator":1, "exit":2, "negative":3, "stairs":4, "toilets":5}
                #0=Cantine, 1=Elevators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
                print "detection results: %f canteen, %f elevators, %f exit, %f no location, %f stairs, %f toilets" % (result[0,0], result[0,1], result[0,2], result[0,3], result[0,4], result[0, 5])
                if result[0, keys[self.audio_location]] > LOCALISATION_TRESHOLD:
                    localisation_success = True
                    print "found location"
                    break
            if localisation_success == True:
                self.say_voiceline("localisation_success")
                self.movement.point_at()
                self.say_voiceline("directions_" + self.audio_location)
                
            else:
                self.say_voiceline("localisation_failed")
            self.movement.finish_movement()
                
        elif self.audio_question == "object_detection":
            self.say_voiceline("object_detection")
            time.sleep(1)
            start = time.time()
            done = False
            timeout = False
            for i in range(0,OBJECT_DETECTION_TRIES):
                while timeout == False and done == False:
                    result = self.vision.classify_object()
                    print "detection results: %f dangerous, %f liquid, %f no object, %f non-dangerous" % (result[0,0], result[0,1], result[0,2], result[0,3])
                    if result[0,0] > DANGEROUS_TRESHOLD:
                        self.say_voiceline("dangerous")
                        done = True
                    elif result[0,3] > NONDANGEROUS_TRESHOLD:
                        self.say_voiceline("nondangerous")
                        done = True
                    elif result[0,1] > LIQUID_TRESHOLD:
                        self.display.show_rules()
                        self.say_voiceline("liquid")
                        done=True
                    if time.time() - start > CLASSIFY_TIMEOUT:
                        self.say_voiceline("no_object")
                        timeout = True
                if done == False and i < OBJECT_DETECTION_TRIES:
                    self.say_voiceline("try_again")
            if done == False:
                self.say_voiceline("object_detection_failed")

    def enable_autonomy(self):
        self.autonomy.setAutonomousAbilityEnabled("All", True)

    def say_voiceline(self, voiceline, data = ""):
        if voiceline == "hello":
            self.audio.say("Hello")
        elif voiceline == "audio_failed":
            self.audio.say("Sorry, I didn't get your question")
        elif voiceline == "localisation":
            self.audio.say("Okay, I will try to find the " + data)
        elif voiceline == "localisation_success":
            self.audio.say("I found it")
        elif voiceline == "localisation_failed":
            self.audio.say("Sorry, I couldn't find it")
        elif voiceline == "directions_stairs":
            self.audio.say("directions to stairs")
        elif voiceline == "directions_canteen":
            self.audio.say("directions to canteen")
        elif voiceline == "directions_elevator":
            self.audio.say("directions to elevator")
        elif voiceline == "directions_toilets":
            self.audio.say("directions to toilets")
        elif voiceline == "directions_exit":
            self.audio.say("directions to exit")
        elif voiceline == "object_detection":
            self.audio.say("Please hold the object in front of my camera")
        elif voiceline == "dangerous":
            self.audio.say("I think this is not allowed")
        elif voiceline == "nondangerous":
            self.audio.say("I think this is okay")
        elif voiceline == "liquid":
            self.audio.say("I think this is a liquid. Please refer to the screen or ask personnel")
        elif voiceline == "no_object":
            self.audio.say("I couldn't detect anything.")
        elif voiceline == "try_again":
            self.audio.say("Please try again")
        elif voiceline == "object_detection_failed":
            self.audio.say("Please ask personnel")
        elif voiceline == "":
            self.audio.say("")
        elif voiceline == "":
            self.audio.say("")
        elif voiceline == "":
            self.audio.say("")
        elif voiceline == "":
            self.audio.say("")
        elif voiceline == "":
            self.audio.say("")
        else:
            self.audio.say(voiceline)
    
    def exit_handler(self):
        print "exiting main()"
                    

Controller()
while True:
   time.sleep(1)