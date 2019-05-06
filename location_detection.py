# Importing libraries
from keras.models import load_model
import numpy as np
from PIL import Image
import tensorflow as tf

class LocationDetection:
    #Desired image sizes used by ImageDataGenerator under training
    IMGWIDTH = 128
    IMGHEIGHT = 96
    trained_cnn = None
    graph = None
     
    def __init__(self, model_path):
        self.trained_cnn = load_model(model_path)
        self.graph = tf.get_default_graph()

    #Function to classify image on trained CNN    
    def classify_image(self, image):
        with self.graph.as_default():
            pil_img = Image.fromarray(image, 'RGB')
            img = pil_img.resize((self.IMGWIDTH,self.IMGHEIGHT))
            img_array = np.array(img)
            img_array = np.expand_dims(img_array, axis=0)
            predictions = self.trained_cnn.predict(img_array)
            #max_index = predictions.argmax(axis=1)
            """text_string = "Cantine: {0:.2f}%, Elevators: {1:.2f}%, Exit: {2:.2f}%, Negatives: {3:.2f}%, Stairs: {4:.2f}%, Negatives: {5:.2f}%".format(result[0,0]*100.0, 
                                                                            result[0,1]*100.0,
                                                                            result[0,2]*100.0,
                                                                            result[0,3]*100.0,
                                                                            result[0,4]*100.0,
                                                                            result[0,5]*100.0)
            print(text_string)
            print('predicted '+ max_index)"""
            return predictions
            #Returns max index of predictions
            #0=Cantine, 1=Elevators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
        
