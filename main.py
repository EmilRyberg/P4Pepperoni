from movement import Movement
from audio import SpeechRecognition
from vision import Vision
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
import threading

PEPPER_IP = "pepper.local"
PEPPER_PORT = 9559

LOCALISATION_TRESHOLD = 0.90
DANGEROUS_TRESHOLD = 0.95
NONDANGEROUS_TRESHOLD = 0.95
LIQUID_TRESHOLD = 0.5

OBJECT_DETECTION_TRIES = 3

GREET_TIMEOUT = 5
GOODBYE_TIMEOUT = 5

class Controller(object):
    def __init__(self):
        session = qi.Session()
        try:
            session.connect("tcp://" + PEPPER_IP + ":" + str(PEPPER_PORT))
        except Exception as e:
            print "[ERROR] Session connect failed"
            sys.exit(1)

        #reenable autonmy in case it got interrupted in the last run
        self.autonomy = session.service("ALAutonomousLife")
        self.autonomy.setAutonomousAbilityEnabled("All", True)
        self.basic_awareness = session.service("ALBasicAwareness")

        self.memory = session.service("ALMemory")
        self.proxy = ALProxy("ALMemory", PEPPER_IP, PEPPER_PORT)

        #init of self made modules
        self.movement = Movement(session)
        self.audio = SpeechRecognition(session, PEPPER_IP, PEPPER_PORT, self.proxy)
        self.vision = Vision(session)
        self.display = Display(session)

        #attempt to stop touch from interrupting program
        self.basic_awareness.setStimulusDetectionEnabled("Touch", False)

        print "\n \n \n" #distance from tensorflow text

        self.audio_question = None
        self.audio_location = None
        self.audio_success = None

        #ensuring hello and goodbye is not said repeatedly
        self.greet_time = time.time()
        self.last_goodbye = 0
        self.goodbye_enabled = True

        #subscribing to people movement
        self.greet_subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone1")
        self.greet_subscriber.signal.connect(self.main_flow)
        self.wave_subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone2")
        self.wave_subscriber.signal.connect(self.greet)
        self.goodbye_subscriber = self.memory.subscriber("EngagementZones/PersonMovedAway")
        self.goodbye_subscriber.signal.connect(self.goodbye)

        #flags for control flow
        self.is_running = False
        self.has_greeted = False
        self.person_left_zone = False

        #setting engagement zone distances
        self.engage = session.service("ALEngagementZones")
        self.engage.setFirstLimitDistance(1)
        self.engage.setSecondLimitDistance(1.5)

        atexit.register(self.exit_handler)

        #making sure pepper responds when there are people already in the zone on program start
        self.people_in_zone_2=len(self.proxy.getData("EngagementZones/PeopleInZone2"))
        self.people_in_zone_1=len(self.proxy.getData("EngagementZones/PeopleInZone1"))
        print "[INFO] Number of people in zone 2: " + str(self.people_in_zone_2)
        print "[INFO] Number of people in zone 1: " + str(self.people_in_zone_1)

        #ready beep
        self.audio.beep.playSine(1000, 40, 0, 0.1)
        time.sleep(0.2)

    #called when people enter zone 1
    def main_flow(self, unused = None):
        print "[INFO] Person entered zone 1"
        if (self.is_running): #making sure only one person can be interacting at a time
            print "[WARNING] Main is already running"
            return
        self.is_running = True
        if self.has_greeted == False: #if someone entered zone 1 without the robot noticing going through zone 2, it needs to say hello anyways
            self.greet()
        print "\n STARTED MAIN FLOW \n"
        self.say_voiceline("How can I help?")
        self.audio_question = None
        time.sleep(0.1)
        while self.audio_question == None and self.are_people_close(): #listen for question for 10 seconds if people are still there
            self.wait_for_question()
        if self.are_people_close(): #check what broke the loop
            self.goodbye_enabled = False #disable goodbye until the answer is finished
            self.respond()
            self.goodbye_enabled = True #reenable goodbye after answer
        else:
            self.is_running = False #if people left mid question, reset state

    #called when people enter zone 2
    def greet(self, unused = None):
        print "[INFO] Person entered zone 2"
        #making sure hello is not too frequent
        if time.time()-self.greet_time > GREET_TIMEOUT:
            self.has_greeted = False
            self.greet_time = time.time()
            #only say hello if no one is currently interacting
            if self.is_running == False:
                self.movement.salute() #wave animation
                self.say_voiceline("hello")
                print "SAID HELLO " + str(time.time())
                self.has_greeted = True
                self.greet_time = time.time()

    #called on people moving further
    def goodbye(self,id):
        #only say goodbye if no one is in zone 1 and 2 and goodbye is enabled at the moment. also making sure goodbye is not too frequent
        if self.goodbye_enabled and not self.are_people_close() and time.time()-self.last_goodbye > GOODBYE_TIMEOUT:
            self.say_voiceline("Goodbye")
            self.last_goodbye = time.time()
            print "[INFO] All zones empty"
        else:
            print "[INFO] Goodbye not enabled right now"

    #routine for getting the question and handling the data
    def wait_for_question(self):
        self.audio_success = False
        question = None
        location = None
        success = None
        question, location, success = self.audio.listen()
        print "[INFO] Speech recognition results: %s, %s, %s" % (question, location, success)
        if success:
            self.audio_success = True
            self.audio_question = question
            self.audio_location = location
        else:
            self.say_voiceline("audio_failed")

    #main function for answering and performing the tasks
    def respond(self):
        if self.audio_question == "localisation": #finding location
            print "[INFO] Localising"
            self.say_voiceline("localisation", self.audio_location)
            localisation_success = False
            self.movement.start_movement() #disable autonomy, put in neutral position
            #start threads to turn and to check if it has done a full turn yet. necessary because the call is blocking and because it sometimes just stops for no reason
            threading.Thread(target=self.movement.continous_turn, args=[15]).start()
            threading.Thread(target=self.movement.check_for_full_turn).start()
            while self.movement.do_move == True:
                result = self.vision.find_location() #run CNN
                keys = {"canteen":0, "elevator":1, "exit":2, "negative":3, "stairs":4, "toilets":5}
                print "[INFO] Detected location: " + keys.keys()[keys.values().index(result)]
                if result == keys[self.audio_location]: #if current one is requested location
                    localisation_success = True
                    print "[INFO] Found location"
                    self.movement.finish_movement() #stop movement, reenable autonomy
                    break
            #check if it was successful
            if localisation_success == True:
                self.say_voiceline("localisation_success")
                self.movement.point_at() #point forward
                self.say_voiceline("directions_" + self.audio_location)
            else:
                self.say_voiceline("localisation_failed")
            self.movement.finish_movement()

        elif self.audio_question == "object_detection": #object classification
            self.enable_autonomy(False) #stop head from moving
            self.say_voiceline("object_detection")
            done = False
            for i in range(0, OBJECT_DETECTION_TRIES): #do a mx number of tries of no object detected
                time.sleep(0.5)
                self.audio.beep.playSine(1000, 40, 0, 0.1) #capture starting beep
                result = self.vision.classify_object() #run CNN
                #Class labels:  {'Cans': 0, 'Headphone': 1, 'Knife': 2, 'Laptop': 3, 'NoObject': 4, 'Phone': 5, 'Pistol': 6,
        #'Scissors': 7, 'SodaPlasticBottle': 8, 'TransparentWaterBottle': 9}
                object_keys = ["cans", "headphones", "knife", "laptop", "no object", "phone", "pistol", "scissors", "soda plastic bottle", "water bottle"]
                print "[INFO] Detection results: " + str(object_keys[int(result)])
                if result != 4: #if it is not 'no object'
                    self.say_voiceline(object_keys[int(result)]) #say appropriate voiceline
                    self.say_voiceline("if unsure")
                    done = True
                    if result == 0 or result == 8 or result == 9: #if result is liquid, display rules also
                        self.display.show_rules()
                    break
                if done == False and i < OBJECT_DETECTION_TRIES-1: #if no object was detected and this is not the last try, say try again
                    self.say_voiceline("try_again")
            if done == False: #if no object was detected too many times in a row
                self.say_voiceline("object_detection_failed")
            self.enable_autonomy(True)
        
        #answer to 'who are you'
        elif self.audio_question == "identification":
            self.say_voiceline("identification")

        self.is_running = False #reset state
        if self.are_people_close(): #if someone is still there, wait for question again
            self.main_flow()
        self.has_greeted = False

    def enable_autonomy(self, enable=True):
        self.autonomy.setAutonomousAbilityEnabled("All", enable)

    #checks if there is anyone in zone 1 and 2
    def are_people_close(self):
        self.people_in_zone_2=len(self.proxy.getData("EngagementZones/PeopleInZone2"))
        self.people_in_zone_1=len(self.proxy.getData("EngagementZones/PeopleInZone1"))
        if self.people_in_zone_1+self.people_in_zone_2:
            return True
        else:
            return False

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
            self.audio.say("Sorry, I couldn't find it. Please ask personnel.")
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
            self.audio.say("Please hold the object in front of my eyes for approximately 5 seconds, while moving it slowly back and forth")
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
        elif voiceline == "identification": #broken up because it would cute before the end of sentence
            self.audio.say("I am the service robot Pepper.") 
            self.audio.say("You can ask me to find the stairs, canteen, elevator, nearest exit and nearest toilet.")
            self.audio.say("I can also help you determine if you can bring a specific object through security")
            time.sleep(1)
        elif voiceline == "cans":
            self.audio.say("I think this is a can. Please refer to the screen or ask personnel")
        elif voiceline == "headphones":
            self.audio.say("I think these are headphones, which are allowed")
        elif voiceline == "knife":
            self.audio.say("I think this is a knife, which is not allowed")
        elif voiceline == "laptop":
            self.audio.say("I think this is a laptop, which is allowed")
        elif voiceline == "no object":
            self.audio.say("I couldn't detect anything")
        elif voiceline == "phone":
            self.audio.say("I think this is a phone, which is allowed")
        elif voiceline == "pistol":
            self.audio.say("I think this is a gun, which is definitely not allowed")
        elif voiceline == "scissors":
            self.audio.say("I think this is a scissor, which is not allowed")
        elif voiceline == "soda plastic bottle":
            self.audio.say("i think this is a plastic soda bottle. Please refer to the screen or ask personnel")
        elif voiceline == "water bottle":
            self.audio.say("I think this is a water bottle. Please refer to the screen or ask personnel")
        elif voiceline == "if unsure":
            self.audio.say("If you think my guess is wrong, please ask personnel")                                                            
        else:
            self.audio.say(voiceline)

    def exit_handler(self):
        print "exiting main()"

#make instance of controller
controller = Controller()

#if there are peope already close, run the appropriate functions
if controller.people_in_zone_2:
    controller.greet(controller.proxy.getData("EngagementZones/PeopleInZone2")[0])
if controller.people_in_zone_1:
    controller.main_flow(controller.proxy.getData("EngagementZones/PeopleInZone1")[0])
#keep program alive
while True:
   time.sleep(1)
