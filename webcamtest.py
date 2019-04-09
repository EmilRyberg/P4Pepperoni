import cv2
from PIL import Image
from localisation import LocalisationCNN
import numpy as np

def main():
    video = cv2.VideoCapture(0)
    cnn = LocalisationCNN()
    
    while True:
        return_value, frame = video.read()
        if not return_value:
            continue
        img = Image.fromarray(frame, 'RGB')
        
        result = cnn.classify_image(img)
        
        #0=Cantine, 1=Elevators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
        if result == 0:
            print('cantine found')
        elif result == 1:
            print('elevators found')
        elif result == 2:
            print('exit found')
        elif result == 4:
            print('stairs found')
        elif result == 5:
            print('toilet found')    
        else:
            print('No known location')
        cv2.imshow("Capturing", frame)
        key=cv2.waitKey(1)
        if key == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()