import naoqi
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import sys
import time
import threading

class Movement(object):
    def __init__(self, session):
        self.session = session

        #Create services
        self.motion_service = self.session.service("ALMotion")
        self.auto_move = self.session.service("ALAutonomousLife")
        self.animation = self.session.service("ALAnimationPlayer")

        self.do_move = False

    #disable autonomy, put head in neutral pose    
    def start_movement(self):
        self.auto_move.setAutonomousAbilityEnabled("All",False)
        self.motion_service.setAngles("HeadYaw", 0, 0.1, async = True)
        self.motion_service.setAngles("HeadPitch", 0, 0.1, async = True)
        self.motion_service.moveInit()
        self.do_move = True

    #try a 360 deg turn at the specified speed
    def continous_turn(self, speed):
        time = 360 / speed
        while self.do_move:
            self.motion_service.moveTo(0,0,6.28, time)

    #stop movement and reenable autonomy
    def finish_movement(self):
        self.do_move = False
        self.motion_service.stopMove()
        self.auto_move.setAutonomousAbilityEnabled("All", True)

    #checks first for the difference of the start angle and current angle to start decresing. This happens when it has turned 180 deg. Then it waits until the difference start increasing again. This happens when it
    #has turned 360 deg
    def check_for_full_turn(self):
		#the True/False parameter is for using MRE sensor values
        start_angle = self.motion_service.getRobotPosition(False)[2]
        time.sleep(0.5)
        difference1 = abs(self.motion_service.getRobotPosition(False)[2]-start_angle)
        time.sleep(0.5)
        while True:
            difference2 = abs(self.motion_service.getRobotPosition(False)[2]-start_angle)
            #print "current angle: %s" % self.motion_service.getRobotPosition(False)[2]
            #print "angle difference: %s" % difference2
            if difference2 < difference1:
                #print "Did full turn"
                #self.do_move = False
                break
            else:
                difference1 = difference2
            time.sleep(0.5)
        while True:
            difference2 = abs(self.motion_service.getRobotPosition(False)[2]-start_angle)
            #print "current angle: %s" % self.motion_service.getRobotPosition(False)[2]
            #print "angle difference: %s" % difference2
            if difference2 > difference1:
                print "Did full turn"
                self.finish_movement()
                break
            else:
                difference1 = difference2
            time.sleep(0.5)        

    #points forward by executing a queue of motions
    def point_at(self):
        direction = 0
        self.motion_service.wakeUp(_async=True)
        self.auto_move.setAutonomousAbilityEnabled("All",False)

		#Set times and stiffness
        joint_times=[[1.0], [2.0], [2.0]]
        is_absolute = True
        stiffness_lists=[[0.3],[0.3], [0.3]]
        stiffness_lists_end=[[0],[0], [0]]
        stiff_times=[[5.0], [5.0], [5.0]]

        self.motion_service.openHand("RHand",_async=True)
        self.motion_service.setStiffnesses("RHand", 0.3)

        joint_list=[["RWristYaw", "RShoulderPitch", "RShoulderRoll"], ["LWristYaw", "LShoulderPtich", "LShoulderRoll"]]

		#Start Trajectory 
        self.motion_service.stiffnessInterpolation(joint_list[direction], stiffness_lists, stiff_times,_async=True)
        self.motion_service.angleInterpolation(joint_list[direction], [[-0.87],[-0.06], [0.24]], joint_times, is_absolute, _async=True)
        self.motion_service.stiffnessInterpolation(joint_list[direction], stiffness_lists_end, stiff_times, _async=True)
        self.auto_move.setAutonomousAbilityEnabled("All",True)
    
    #wave gesture
    def salute(self):
        threading.Thread(target=self.salute_async_execute).start()

    def salute_async_execute(self):
        self.animation.run("animations/Stand/Gestures/Hey_1")