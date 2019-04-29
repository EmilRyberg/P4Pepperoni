import cv2
from PIL import Image
from localisation import LocalisationCNN
import numpy as np
from matplotlib import pyplot as plt

def main():
    video = cv2.VideoCapture(0)
    cnn = LocalisationCNN()
    iteration = 0;
    
    while True:
        return_value, frame = video.read()
        if not return_value:
            continue
        img = Image.fromarray(frame, 'RGB')
        if iteration % 120 == 0:
            resized = np.array(img.resize((128,96)))
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            #plt.subplot(331)
            plt.imshow(resized)
            plt.show()
        
        result = cnn.classify_image(img)
        print(result)
        #0=Cantine, 1=Elevators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
        if result[0] == 0 and result[1] > 0.8:
            print('cantine found')
        elif result[0] == 1 and result[1] > 0.8:
            print('elevators found')
        elif result[0] == 2 and result[1] > 0.8:
            print('exit found')
        elif result[0] == 4 and result[1] > 0.8:
            print('stairs found')
        elif result[0] == 5 and result[1] > 0.8:
            print('toilet found')    
        else:
            print('No known location')
        cv2.imshow("Capturing", frame)
        key=cv2.waitKey(1)
        iteration += 1
        if key == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()