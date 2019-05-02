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
        textStr = "Cantine: {0:.2f}%, Elevators: {1:.2f}%,".format(result[0,0]*100.0, 
                                                            result[0,1]*100.0)
        textStr2 = "Exit: {0:.2f}%, Negatives: {1:.2f}%".format(result[0,2]*100.0, result[0,3]*100.0)
        textStr3 = "Stairs: {0:.2f}%, Negatives: {1:.2f}%".format(result[0,4]*100.0, result[0,5]*100.0)
        cv2.putText(frame, textStr, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, textStr2, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, textStr3, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow("Capturing", frame)
        key=cv2.waitKey(1)
        if key == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main('localisation_cnn.h5')