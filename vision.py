import numpy as np
from location_detection import LocationDetection
from object_detection import ObjectDetection
import time
import atexit
import random

class Vision:
    subscribeId = "vision" + str(random.randint(1,100000))

    def __init__(self, session):
        self.session = session
        self.localisation_cnn = LocationDetection('localisation_cnn.h5')
        self.object_detection = ObjectDetection('object_detection_model.hdf5')
        self.vid_service = self.session.service('ALVideoDevice')
                
        # subscribe to the top camera
        AL_kTopCamera = 0
        AL_kVGA = 2  # 640x480
        AL_kBGRColorSpace = 13
        self.capture_device = self.vid_service.subscribeCamera(self.subscribeId, AL_kTopCamera, AL_kVGA, AL_kBGRColorSpace, 10)
        atexit.register(self.exit_handler)
    
    def __del__(self):
        self.vid_service.unsubscribe(self.subscribeId)
        print "unsubscribed from camera"
            
    def classify_object(self):
        # creating an empty image of size 640x480
        width = 640
        height = 480
        image = np.zeros((height, width, 3), np.uint8)
        summed_predictions = None
        
        for j in range(11): #We take 11 images, in order to predict whatever predictions occurs the most imtes
            for i in range(60): #Retries up to 60 times to get an image from Pepper
                # Getting an image remotely from Pepper
                result = self.vid_service.getImageRemote(self.capture_device)
                if result != None:
                    break
                time.sleep(0.1)
            
            # Checking if result is empty or broken
            if result == None:
                print('cannot capture.')
            elif result[6] == None:
                print('no image data string.')
            else:
                # converts the data into a numpy array
                values = map(ord, str(bytearray(result[6])))
                index = 0
                for y in range(0, height):
                    for x in range(0, width):
                        image.itemset((y, x, 0), values[index + 0])
                        image.itemset((y, x, 1), values[index + 1])
                        image.itemset((y, x, 2), values[index + 2])
                        index += 3
                
                # now the image will be cropped to be square (since CNN is trained on square images,
                # and borders are not important anyways)
                width_height_difference = width - height
                width_to_cut = int(width_height_difference / 2)
                croppedImage = image[0:image.shape[0], width_to_cut:image.shape[1]-width_to_cut]
                result = self.object_detection.predict_certainties(croppedImage)

                # add the prediction vector to the previous predictions
                if (j == 0): 
                    summed_predictions = result
                else:
                    summed_predictions = summed_predictions + result
        
        print "Summed predictions: %s" % (str(summed_predictions)) # Used for debugging
        return np.argmax(summed_predictions, axis = 1) # Return the most occuring prediction in the summed predictions
            
            
    def find_location(self):
        # creating an empty image of size 640x480
        width = 640
        height = 480
        image = np.zeros((height, width, 3), np.uint8)
        summed_predictions = None
        #Takes three images, checks for the most frequent location and returns that as the 'average location'
        for j in range(3):
            for i in range(60):
                # Getting an image
                result = self.vid_service.getImageRemote(self.capture_device)
                if result != None:
                    break
                time.sleep(0.1)
            
            # Checking if result is empty or broken
            if result == None:
                print('cannot capture.')
            elif result[6] == None:
                print('no image data string.')
            else:
                # Not sure if below is useful, test.
                #translate value to mat
                values = map(ord, str(bytearray(result[6])))
                # print(values) used for debugging
                index = 0
                for y in range(0, height):
                    for x in range(0, width):
                        #image.itemset((y, x, 0), values[i+0])
                        image.itemset((y, x, 0), values[index + 0])
                        image.itemset((y, x, 1), values[index + 1])
                        image.itemset((y, x, 2), values[index + 2])
                        index += 3
                predicted_location = self.localisation_cnn.classify_image(image)
                if (j == 0):
                    summed_predictions = predicted_location
                else:
                    summed_predictions = summed_predictions + predicted_location
        print (summed_predictions.shape)
        average_prediction = summed_predictions.argmax(axis = 1)
        return average_prediction #Returns the most frequent observed location

    def exit_handler(self):
        self.vid_service.unsubscribe(self.subscribeId)
        print "unsubscribed from camera"
