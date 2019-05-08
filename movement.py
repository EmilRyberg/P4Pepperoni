import naoqi
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import sys
import time
import threading

PEPPER_IP = "pepper.local"

PEPPER_PORT = 9559

class Movement(object):
    """Movement Module"""
    def __init__(self, session):
        self.session = session

        #Create services
        self.memory = self.session.service("ALMemory")
        self.tts = self.session.service("ALTextToSpeech")
        self.motion_service = self.session.service("ALMotion")
        self.basic_awareness = self.session.service("ALBasicAwareness")
        self.auto_move = self.session.service("ALAutonomousLife")
        self.engage = self.session.service("ALEngagementZones")
        self.perception = self.session.service("ALPeoplePerception")
        self.animation = self.session.service("ALAnimationPlayer")

        self.do_move = False
        
    def start_movement(self):
        self.auto_move.setAutonomousAbilityEnabled("All",False)
        self.motion_service.setAngles("HeadYaw", 0, 0.1, async = True)
        self.motion_service.setAngles("HeadPitch", 0, 0.1, async = True)
        self.motion_service.moveInit()


    def turn(self, degrees, speed):
        self.move_done = False
        print "turning"
        time = degrees / speed
        self.motion_service.moveTo(0,0, 0.5*degrees*0.0174533, 0.5*time)
        self.motion_service.moveTo(0,0, 0.5*degrees*0.0174533, 0.5*time)
        print "turning done"
        self.move_done = True

    def continous_turn(self, speed):
        time = 360 / speed
        while self.do_move:
            self.motion_service.moveTo(0,0,6.28, time)

    def finish_movement(self):
        self.do_move = False
        self.motion_service.stopMove()
        self.auto_move.setAutonomousAbilityEnabled("All", True)

    def check_for_full_turn(self):
        start_angle = self.motion_service.getRobotPosition(False)[2]
        time.sleep(0.5)
        difference1 = abs(self.motion_service.getRobotPosition(False)[2]-start_angle)
        time.sleep(0.5)
        while True:
            difference2 = abs(self.motion_service.getRobotPosition(False)[2]-start_angle)
            print "angle difference: %s" % difference2
            if difference2 < difference1:
                print "Did full turn"
                self.do_move = False
                break
            else:
                difference1 = difference2
            time.sleep(0.5)

    def point_at(self):
        direction = 0
        self.motion_service.wakeUp(_async=True)
        self.auto_move.setAutonomousAbilityEnabled("All",False)

        joint_times=[[1.0], [2.0], [2.0]]
        is_absolute = True
        stiffness_lists=[[0.3],[0.3], [0.3]]
        stiffness_lists_end=[[0],[0], [0]]
        stiff_times=[[5.0], [5.0], [5.0]]

        self.motion_service.openHand("RHand",_async=True)
        self.motion_service.setStiffnesses("RHand", 0.3)

        joint_list=[["RWristYaw", "RShoulderPitch", "RShoulderRoll"], ["LWristYaw", "LShoulderPtich", "LShoulderRoll"]]

        self.motion_service.stiffnessInterpolation(joint_list[direction], stiffness_lists, stiff_times,_async=True)
        self.motion_service.angleInterpolation(joint_list[direction], [[-0.87],[-0.06], [0.24]], joint_times, is_absolute, _async=True)
        self.motion_service.stiffnessInterpolation(joint_list[direction], stiffness_lists_end, stiff_times, _async=True)
        self.auto_move.setAutonomousAbilityEnabled("All",True)



    
    def point_at_old(self, location, direction):

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
        threading.Thread(target=self.salute_async_execute).start()

    def salute_async_execute(self):
        self.animation.run("animations/Stand/Gestures/Hey_1")

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

move = Movement(session)

move.auto_move.setAutonomousAbilityEnabled("All",False)
move.motion_service.setAngles("HeadYaw", 0, 0.1, async = True)
move.motion_service.setAngles("HeadPitch", 0, 0.1, async = True)
move.motion_service.moveInit()

start_angle = move.motion_service.getRobotPosition(False)[2]
if start_angle < 0:
    start_angle += 6.28
print "start angle %s" % start_angle

current_angle = start_angle
temp1 = 0
temp2 = 0

do_turn = True

while do_turn:
    move.motion_service.moveTo(0,0,0.017*180, 12)
    current_angle = move.motion_service.getRobotPosition(False)[2]
    if current_angle < 0:
        current_angle += 6.28
    temp1 = current_angle-start_angle
    print "turned so far %s" % turned_so_far  
    print "current pos %s" % move.motion_service.getRobotPosition(False)


#    2 3 4 5 6 1 2 3 4 5