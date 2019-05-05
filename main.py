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
import random

PEPPER_IP = "pepper.local"
PEPPER_PORT = 9559

LOCALISATION_TRESHOLD = 0.90
DANGEROUS_TRESHOLD = 0.95
NONDANGEROUS_TRESHOLD = 0.95
LIQUID_TRESHOLD = 0.5

OBJECT_DETECTION_TRIES = 3

GREET_TIMEOUT = 5

class Controller(object):
    def __init__(self):
        session = qi.Session()
        try:
            session.connect("tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT))
            #app = qi.Application(["SayHi", "--qi-url=" + "tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT)])
        except RuntimeError:
            print("session connect failed")
            sys.exit(1)

        self.autonomy = session.service("ALAutonomousLife")
        self.autonomy.setAutonomousAbilityEnabled("All", True)

        self.movement = Movement(session)
        self.audio = SpeechRecognition(session, PEPPER_IP, PEPPER_PORT)
        self.vision = VisionModule(session)
        self.display = Display(session)

        self.audio_question = None
        self.audio_location = None
        self.audio_success = None

        self.greet_time = time.time()

        self.memory = session.service("ALMemory")
        self.proxy = ALProxy("ALMemory", PEPPER_IP, PEPPER_PORT)
        self.beep = ALProxy("ALAudioDevice", PEPPER_IP, PEPPER_PORT)

        self.greet_subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone1")
        self.greet_subscriber.signal.connect(self.main_flow)
        self.wave_subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone2")
        self.wave_subscriber.signal.connect(self.greet)
        self.goodbye_subscriber = self.memory.subscriber("EngagementZones/PersonMovedAway")
        self.goodbye_subscriber.signal.connect(self.goodbye)
        self.is_running = False
        self.has_greeted = False

        self.engage = session.service("ALEngagementZones")
        self.engage.setFirstLimitDistance(0.75)
        self.engage.setSecondLimitDistance(1.5)

        atexit.register(self.exit_handler)

        self.people_in_zone_2=len(self.proxy.getData("EngagementZones/PeopleInZone2"))
        self.people_in_zone_1=len(self.proxy.getData("EngagementZones/PeopleInZone1"))
        print "[INFO] Number of people in zone 2: " + str(self.people_in_zone_2)
        print "[INFO] Number of people in zone 1: " + str(self.people_in_zone_1)

        self.beep.playSine(1000, 40, 0, 0.1)
        time.sleep(0.2)

    def main_flow(self, unused = None):
        print "[INFO] Person entered zone 1"
        if (self.is_running):
            print "[WARNING] Main is already running"
            return
        self.is_running = True
        if self.has_greeted == False:
            self.greet()
        print "STARTED MAIN FLOW"
        self.say_voiceline("Ready")
        self.audio_question = None
        time.sleep(0.5)
        while (self.audio_question == None):
            print "CALLED AUDIO LISTEN"
            while(self.wait_for_question() == False):
                continue
        if self.audio_success == False:
            return
        self.respond()

    def greet(self, id, unused = None):
        print "[INFO] Person entered zone 2"
        self.person_id = id
        if (time.time()-self.greet_time > GREET_TIMEOUT):
            self.has_greeted = False
        if (self.is_running == False):
            self.movement.salute()
            self.say_voiceline("hello")
            self.has_greeted = True
            self.greet_time = time.time()

    def goodbye(self,id):
        if id == self.person_id:
            self.say_voiceline("Goodbye")

    def wait_for_question(self):
        self.audio_success = False
        for i in range(0, 3):
            question = None
            location = None
            success = None
            try:
                question, location, success = self.audio.listen()
            except Exception as e:
                print "audio listen failed: " + str(e)
                return False
            print "Speech stuff: %s, %s, %s" % (question, location, success)
            if success:
                self.audio_success = True
                self.audio_question = question
                self.audio_location = location
                break
            else:
                self.say_voiceline("audio_failed")
        return True

    def respond(self):
        if self.audio_question == "localisation":
            print "localising"
            self.say_voiceline("localisation", self.audio_location)
            self.movement.start_movement()
            localisation_success = False
            for i in range(0, 30/15):
                self.movement.turn(15, 600)
                result = self.vision.find_location()
                #result = [0,0,0,0,0,0]
                keys = {"canteen":0, "elevator":1, "exit":2, "negative":3, "stairs":4, "toilets":5}
                #0=Cantine, 1=Elevators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
                print "detection results: %f canteen, %f elevators, %f exit, %f no location, %f stairs, %f toilets" % (result[0,0], result[0,1], result[0,2], result[0,3], result[0,4], result[0, 5])
                if result[0, keys[self.audio_location]] > LOCALISATION_TRESHOLD: #FIX THIS AS WE DON'T HAVE A THRESHOLD ANYWAY
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
            done = False
            time.sleep(0.5)
            self.enable_autonomy(False)
            self.beep.playSine(1000, 40, 0, 0.1)
            for i in range(0,OBJECT_DETECTION_TRIES):
                time.sleep(1.5)
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
                if done == False and i < OBJECT_DETECTION_TRIES:
                    self.say_voiceline("try_again")
            if done == False:
                self.say_voiceline("object_detection_failed")
            self.enable_autonomy(True)

        self.is_running = False
        self.has_greeted = False

    def enable_autonomy(self, enable=True):
        self.autonomy.setAutonomousAbilityEnabled("All", enable)

    def say_voiceline(self, voiceline, data = ""):
        if voiceline == "hello":
            i = random.randint(0,3)
            if i == 0:
                self.audio.say("Hello")
            elif i == 1:
                self.audio.say("Fuck off")
            elif i == 2:
                self.audio.say("Move away, cunt")
            elif i == 3:
                self.audio.say("Retard")
        elif voiceline == "audio_failed":
            self.audio.say("Sorry, I didn't get your question")
        elif voiceline == "localisation":
            self.audio.say("Okay, I will try to find the " + data)
        elif voiceline == "localisation_success":
            self.audio.say("I found it")
        elif voiceline == "localisation_failed":
            self.audio.say("Sorry, I couldn't find it")
        elif voiceline == "directions_stairs":
            self.audio.say("You will find the stairs right over there, by the tree")
        elif voiceline == "directions_canteen":
            self.audio.say("You will find the canteen over there, on the other side of this floor")
        elif voiceline == "directions_elevator":
            self.audio.say("You will find the elevator around the corner over there by the red wall")
        elif voiceline == "directions_toilets":
            self.audio.say("You will find the toilet over there. Just take the second door on your left") #Double check it's the second door
        elif voiceline == "directions_exit":
            self.audio.say("You will find the nearest exit right around the corner")
        elif voiceline == "object_detection":
            self.audio.say("Please hold the object in front of my camera for approximately 5 seconds")
        elif voiceline == "dangerous":
            self.audio.say("I don't think this is allowed through security")
        elif voiceline == "nondangerous":
            self.audio.say("I think you are allowed to bring the through security")
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


controller = Controller()
if controller.people_in_zone_2:
    controller.greet()
if controller.people_in_zone_1:
    controller.main_flow()
while True:
   time.sleep(1)
