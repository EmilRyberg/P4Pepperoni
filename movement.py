import naoqi
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import sys
import time

PEPPER_IP = "192.168.1.15"

PEPPER_PORT = 9559
loc_names=["toilets", "canteen","stairs", "elevator", "exit"]
location = 1 #TO BE CHANGED. just so that my compiler doesnt scream

class Movement(object):
    """Movement Module"""
    def __init__(self, session):
        #super(Movement, self).__init__()
        self.session = session
        #ALModule.__init__(self)
        """super makes the class inherit the methods from init and connects to ALModule
        TO REVISE"""

        #Create services
        self.memory = self.session.service("ALMemory")
        self.tts = self.session.service("ALTextToSpeech")
        self.motion_service = self.session.service("ALMotion")
        self.basic_awareness = self.session.service("ALBasicAwareness")
        self.auto_move = self.session.service("ALAutonomousLife")
        self.engage = self.session.service("ALEngagementZones")
        self.perception = self.session.service("ALPeoplePerception")
        self.animation = self.session.service("ALAnimationPlayer")


        #Subscribe to Events

        #self.subscriber = self.memory.subscriber("EngagementZones/PersonEnteredZone1")
        #self.subscriber.signal.connect(self.salute)
        

        #List declaration (put here variables?)

        #Stuff that might or might not be needed
        #super(Movement, self).__init__()
        #self.face_detection.subscribe("HumanGreeter")
        #self.engage.subscribe("HumanGreeter")
    
    def looking_for(self, location, cnn_working):

        self.auto_move.setAutonomousAbilityEnabled("All",False, async = True)
        self.motion_service.setAngles("HeadYaw", 0, 0.1, async = True)
        self.motion_service.setAngles("HeadPitch", 0, 0.1, async = True)
        self.motion_service.moveTo(0,0, -3.14/2,2)
        

        position_vector1 = self.motion_service.getRobotPosition(True)

        self.tts.say("I will start looking for the" + loc_names[location])

        cnn_working = True #For now


        while cnn_working:
            self.auto_move.setAutonomousAbilityEnabled("All",False)
            self.motion_service.moveTo(0,0, 0.087, 0.5) #x, y, rotz and time to reach to that position
            position_vector2 = self.motion_service.getRobotPosition(True)

            diff = position_vector2[2]-position_vector1[2]
            angle_range = abs(diff) 
        
            if angle_range>=3.14 and cnn_working: #180degrees from initial position
                self.tts.say("sorry, I couldn't find the "+ loc_names[location] )
                time.sleep(1)
                self.auto_move.setAutonomousAbilityEnabled("All",True)
                cnn_working = False
                #break, call next function, up to main controller
        

    
    def point_at(self, location, direction):

        #Set stiffness and disable autonomous life(otherwise doesnt work well)
        self.motion_service.wakeUp(_async=True)
        self.auto_move.setAutonomousAbilityEnabled("All",False)

        #For right, direction =0, for left, direction =1
        #List of directions, joints and angle for each location MOVE TO INIT?
        hand_open=["RHand", "LHand"]    
        joint_list=[["RWristYaw", "RShoulderPitch", "RShoulderRoll"], ["LWristYaw", "LShoulderPtich", "LShoulderRoll"]]
        angle_list=[["""toiletangles"""], [[-0.87],[-0.06], [0.24]], ["""stairsangles"""], ["""elevatorangles"""]]
        loc_names=["toilets", "canteen","stairs", "elevator"]

        #Set times and stiffness
        joint_times=[[1.0], [2.0], [2.0]]
        is_absolute = True
        stiffness_lists=[[0.3],[0.3], [0.3]]
        stiff_times=[[5.0], [5.0], [5.0]]

        #Start opening hand

        self.motion_service.openHand(hand_open[direction],_async=True)
        self.motion_service.setStiffnesses(hand_open[direction], 0.3)
    

        #Start Trajectory 
        
        self.motion_service.stiffnessInterpolation(joint_list[direction], stiffness_lists, stiff_times,_async=True)
        self.motion_service.angleInterpolation(joint_list[direction], angle_list[location], joint_times, is_absolute, _async=True)
        self.tts.say("The"+ loc_names[location]+ "is in that direction")
        time.sleep(5)

        #Restart Autonomous life MAYBE?
        self.auto_move.setAutonomousAbilityEnabled("All",True)

    def salute(self):
        self.animation.run("animations/Stand/Gestures/Hey_1")
        #self.memory.unsubscribe("EngagementZones/PersonEnteredZone1")


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
   
   
    #main(session)

    #engage_ment = SayHi(app)
    #engage_ment.run()



#Previous functions (JUST IN CASE)
