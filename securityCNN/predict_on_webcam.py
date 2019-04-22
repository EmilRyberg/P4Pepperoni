# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:19:00 2019

@author: Emil
"""

import cv2
import numpy as np
from PIL import Image
from keras import models
import argparse

def main(model_name):
    model = models.load_model(model_name)
    video = cv2.VideoCapture(0)
    while True:
        _, frame = video.read()
        
        img = Image.fromarray(frame, 'RGB')

        img = img.resize((160,160))
        img_array = np.array(img)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

        #Our keras model used a 4D tensor, (images x height x width x channel)
        #So changing dimension 128x128x3 into 1x128x128x3 
        img_array = np.expand_dims(img_array, axis=0)

        #Calling the predict method on model to predict 'me' on the image
        predictions = model.predict(img_array)
        #print ('Predictions: ', predictions)
        max_index = predictions.argmax(axis=1)
        #Class labels:  {'Dangerous': 0, 'Liquid': 1, 'NoObject': 2, 'NonDangerous': 3}
        textStr = "Dangerous: {0:.2f}%, Liquid: {1:.2f}%, NoObject: {2:.2f}%, NonDangerous: {3:.2f}%".format(predictions[0,0]*100.0, 
                                                                          predictions[0,1]*100.0, 
                                                                          predictions[0,2]*100.0,
                                                                          predictions[0,3]*100.0)
        cv2.putText(frame, textStr, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow("Capturing", frame)
        key=cv2.waitKey(1)
        if key == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predicts on webcam')
    parser.add_argument('model', type=str,
                       help='the model to use for detecting objects')
    
    args = parser.parse_args()
    main(args.model)