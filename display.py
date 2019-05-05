from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import qi
import sys
import time
import threading

class Display(object):
    def __init__(self, session):
        self.session = session
        self.tabletService = self.session.service("ALTabletService")

    def show_rules(self):
        threading.Thread(target=self.show_image_async).start()

    def show_image_async(self):
        self.tabletService.setBrightness(1)
        self.tabletService.showImage("https://www.bristolairport.co.uk/~/media/images/brs/pages/at-the-airport/security-liquids-v2.ashx?h=418&w=400&la=en&hash=30A47A77FD953CE417F687833D2BA1FB8378714B")
        time.sleep(10)
        self.tabletService.hideImage()
        self.tabletservice.setBrightness(0.2)
