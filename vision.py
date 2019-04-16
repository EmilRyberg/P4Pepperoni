import numpy as np
from localisation import LocalisationCNN
from EMILSPATH import EMILSCLASS
from movementV1 import MovementClass

class VisionModule:
      session = None
      def __init__(self, session):
            self.session = session
            
      def classify_object(self):
          vid_service = self.session.service('ALVideoDevice')
          # subscribe to the top camera
          AL_kTopCamera = 0
          AL_kVGA = 2  # 640x480
          AL_kBGRColorSpace = 13
          captureDevice = vid_service.subscribeCamera(
              "vision", AL_kTopCamera, AL_kVGA, AL_kBGRColorSpace, 10)

          # creating an empty image of size 640x480
          width = 640
          height = 480
          image = np.zeros((height, width, 3), np.uint8)

          # Getting an image
          result = vid_service.getImageRemote(captureDevice)
          
          # Checking if result is empty or broken
          if result == None:
              print('cannot capture.')
          elif result[6] == None:
              print('no image data string.')
          else:
              # Not sure if below is useful, test.
              #translate value to mat
              values = map(ord, str(bytearray(result[6])))
              # print(values)
              i = 0
              for y in range(0, height):
                  for x in range(0, width):
                      #image.itemset((y, x, 0), values[i+0])
                      image.itemset((y, x, 0), values[i + 0])
                      image.itemset((y, x, 1), values[i + 1])
                      image.itemset((y, x, 2), values[i + 2])
                      i += 3
              result = EMILSCLASS.EMILSCLASSIFIER(image)
              return result
            
            
      def find_localisation(self, localisation):
                vid_service = self.session.service('ALVideoDevice')
                # subscribe to the top camera
                AL_kTopCamera = 0
                AL_kVGA = 2  # 640x480
                AL_kBGRColorSpace = 13
                CaptureDevice = vid_service.subscribeCamera(
                    "vision", AL_kTopCamera, AL_kVGA, AL_kBGRColorSpace, 10)

                # creating an empty image of size 640x480
                width = 640
                height = 480
                image = np.zeros((height, width, 3), np.uint8)

                # Getting an image
                PepperImage = vid_service.getImageRemote(CaptureDevice)
          
                # Checking if result is empty or broken
                if PepperImage == None:
                  print('cannot capture.')
                elif PepperImage[6] == None:
                  print('no image data string.')
                else:
                  # Not sure if below is useful, test.
                  #translate value to mat
                  values = map(ord, str(bytearray(PepperImage[6])))
                  # print(values) used for debugging
                  i = 0
                  for y in range(0, height):
                      for x in range(0, width):
                          #image.itemset((y, x, 0), values[i+0])
                          image.itemset((y, x, 0), values[i + 0])
                          image.itemset((y, x, 1), values[i + 1])
                          image.itemset((y, x, 2), values[i + 2])
                          i += 3
                  result = LocalisationCNN.classify_image(image)
                  return result #Returns array of 2, where [0]=location [1]=certainty
