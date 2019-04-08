import cv2
from PIL import Image
from localisation import LocalisationCNN

def main():
    video = cv2.VideoCapture(0)
    while True:
        _, frame = video.read()
        
        img = Image.fromarray(frame, 'RGB')
        
        result = LocalisationCNN.classify_image(img)
        
        #0=Cantine, 1=Elavators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
        if result == 0:
            print('cantine found')
        elif result == 1:
            print('elavators found')
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