import numpy as np
from localisation import LocalisationCNN
from object_detection import ObjectDetection

class VisionModule:
    session = None
    localisation_cnn = LocalisationCNN('localisation_cnn.h5')
    object_detection = ObjectDetection('object_detection_model.hdf5')
    def __init__(self, session):
        self.session = session
            
    def classify_object(self):
        vid_service = self.session.service('ALVideoDevice')
        # subscribe to the top camera
        AL_kTopCamera = 0
        AL_kVGA = 2  # 640x480
        AL_kBGRColorSpace = 13
        capture_device = vid_service.subscribeCamera(
            "vision", AL_kTopCamera, AL_kVGA, AL_kBGRColorSpace, 10)

        # creating an empty image of size 640x480
        width = 640
        height = 480
        image = np.zeros((height, width, 3), np.uint8)

        # Getting an image
        result = vid_service.getImageRemote(capture_device)
          
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
            result = self.object_detection.predict_certainties(image)
            return result
            
            
    def find_localisation(self):
        vid_service = self.session.service('ALVideoDevice')
        # subscribe to the top camera
        AL_kTopCamera = 0
        AL_kVGA = 2  # 640x480
        AL_kBGRColorSpace = 13
        capture_device = vid_service.subscribeCamera(
                "vision", AL_kTopCamera, AL_kVGA, AL_kBGRColorSpace, 10)

        # creating an empty image of size 640x480
        width = 640
        height = 480
        image = np.zeros((height, width, 3), np.uint8)

        # Getting an image
        pepper_image = vid_service.getImageRemote(capture_device)
          
        # Checking if result is empty or broken
        if pepper_image == None:
            print('cannot capture.')
        elif pepper_image[6] == None:
            print('no image data string.')
        else:
            # Not sure if below is useful, test.
            #translate value to mat
            values = map(ord, str(bytearray(pepper_image[6])))
            # print(values) used for debugging
            i = 0
            for y in range(0, height):
                for x in range(0, width):
                    #image.itemset((y, x, 0), values[i+0])
                    image.itemset((y, x, 0), values[i + 0])
                    image.itemset((y, x, 1), values[i + 1])
                    image.itemset((y, x, 2), values[i + 2])
                    i += 3
            result = self.localisation_cnn.classify_image(image)
            return result #Returns array of 2, where [0]=location [1]=certainty
