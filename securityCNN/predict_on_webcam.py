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
        width_height_difference = frame.shape[1] - frame.shape[0]
        width_to_cut = int(width_height_difference / 2)
        cropped_frame = frame[0:frame.shape[0], width_to_cut:frame.shape[1]-width_to_cut]
        
        img = Image.fromarray(cropped_frame, 'RGB')

        img = img.resize((200,200))
        img_array = np.array(img)
        #img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        img_array = np.expand_dims(img_array, axis=0)

        #Calling the predict method on model to predict 'me' on the image
        predictions = model.predict(img_array)
        #print ('Predictions: ', predictions)
        #max_index = predictions.argmax(axis=1)
        #Class labels:  {'Cans': 0, 'Headphone': 1, 'Knife': 2, 'Laptop': 3, 'NoObject': 4, 'Phone': 5, 'Pistol': 6,
        #'Scissors': 7, 'SodaPlasticBottle': 8, 'TransparentWaterBottle': 9}
        text_str = "Cans: {0:.2f}% - Headphone: {1:.2f}%".format(predictions[0, 0] * 100.0, 
                                                                          predictions[0, 1] * 100.0)
        text_str_2 = "Knife: {0:.2f}% - Laptop: {1:.2f}%".format(predictions[0, 2] * 100.0, predictions[0, 3] * 100.0)
        text_str_3 = "NoObject: {0:.2f}% - Phone: {1:.2f}%".format(predictions[0, 4] * 100.0, predictions[0, 5] * 100.0)
        text_str_4 = "Pistol: {0:.2f}% - Scissors: {1:.2f}%".format(predictions[0, 6] * 100.0, predictions[0, 7] * 100.0)
        text_str_5 = "SodaBottle: {0:.2f}% - WaterBottle: {1:.2f}%".format(predictions[0, 8] * 100.0, predictions[0, 9] * 100.0)
        text_lines = [text_str, text_str_2, text_str_3, text_str_4, text_str_5]
        for i in range(len(text_lines)):
            cv2.putText(cropped_frame, text_lines[i], (10, 20 + (i * 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)

        cv2.imshow("Capturing", cropped_frame)
        cv2.imshow("Resized", np.squeeze(img_array, axis=0))
        key = cv2.waitKey(1)
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