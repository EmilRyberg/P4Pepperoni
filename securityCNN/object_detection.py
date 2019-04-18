# -*- coding: utf-8 -*-

from keras import models
from PIL import Image
import numpy as np
import cv2

class ObjectDetection:
    model = None
    def __init__(self, model_file_path):
        models.load_model(model_file_path)
        
    """image should be a numpy array, returns numpy array with probabilities for each class"""
    def predict_probabilities(self, image):
        img = Image.fromarray(image, 'RGB')

        img = img.resize((160,160))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        predictions = self.model.predict(img_array)
        return predictions

