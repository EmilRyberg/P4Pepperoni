# -*- coding: utf-8 -*-

from keras import models
from PIL import Image
import numpy as np
import tensorflow as tf

class ObjectDetection:
    def __init__(self, model_file_path):
        self.model = models.load_model(model_file_path)
        self.graph = tf.get_default_graph()
        
        
    """image should be a numpy array, returns numpy array with probabilities for each class"""
	#Class labels:  {'Dangerous': 0, 'Liquid': 1, 'NoObject': 2, 'NonDangerous': 3}
    def predict_certainties(self, image):
        with self.graph.as_default():
            img = Image.fromarray(image, 'RGB')
			#Resizes image, into array, predicts
            img = img.resize((200,200))
            img_array = np.array(img)
            img_array = np.expand_dims(img_array, axis=0)
            predictions = self.model.predict(img_array)
            return predictions

