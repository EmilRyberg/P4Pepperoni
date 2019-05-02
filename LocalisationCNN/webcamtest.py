import cv2
from PIL import Image
import numpy as np
from keras.models import load_model

def main(model_file_path):
    trained_cnn = load_model(model_file_path)
    video = cv2.VideoCapture(0)
    
    while True:
        return_value, frame = video.read()
        if not return_value:
            continue
        img = Image.fromarray(frame, 'RGB')
        resized = np.array(img.resize((128,96)))
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        resized = np.expand_dims(resized, axis=0)
        
        result = trained_cnn.predict(resized)
        #max_index = result.argmax(axis=1)
        text_string = "Cantine: {0:.2f}%, Elevators: {1:.2f}%, Exit: {2:.2f}%, Negatives: {3:.2f}%, Stairs: {4:.2f}%, Negatives: {5:.2f}%".format(result[0,0]*100.0, 
                                                                            result[0,1]*100.0,
                                                                            result[0,2]*100.0,
                                                                            result[0,3]*100.0,
                                                                            result[0,4]*100.0,
                                                                            result[0,5]*100.0)
        print(text_string)
        cv2.imshow("Capturing", frame)
        key=cv2.waitKey(1)
        if key == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main('localisation_cnn.h5')