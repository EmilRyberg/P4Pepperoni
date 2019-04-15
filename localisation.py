# Importing libraries
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import cv2
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

class LocalisationCNN:
      #Desired image sizes used by ImageDataGenerator under training
      IMGWIDTH = 128
      IMGHEIGHT = 96
      trained_cnn = None
      
#      def __init__(self):
#          self.trained_cnn = load_model('localisation_cnn.h5')
      
      # Building the CNN
      def build_cnn(self, ImgWidth, ImgHeight):
          #Initialising the CNN
          cnn = Sequential()
          #First Conv+Pool layer
          cnn.add(Conv2D(32, (3, 3), input_shape = (ImgHeight, ImgWidth, 3), activation = 'relu'))
          cnn.add(MaxPooling2D(pool_size = (2, 2)))
          #Second Conv+Pool layer
          cnn.add(Conv2D(32, (3, 3), activation = 'relu'))
          cnn.add(MaxPooling2D(pool_size = (2, 2)))
          #Third Conv+Pool layer
          cnn.add(Conv2D(32, (3, 3), activation = 'relu'))
          cnn.add(MaxPooling2D(pool_size = (2, 2)))
          #Flattening
          cnn.add(Flatten())
      
          #Fully connected layers
          cnn.add(Dense(64, activation='relu'))
          cnn.add(Dense(64, activation='relu'))
          cnn.add(Dense(64, activation='relu'))
          cnn.add(Dense(units = 6, activation = 'softmax'))
      
          #Compiling the CNN
          cnn.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])  
          
          return cnn
        
      #Fitting the CNN to the training images
      def train_cnn(self, bs, epochs):
          train_datagen = ImageDataGenerator(rescale = 1./255,
                                         shear_range = 0.2,
                                         zoom_range = 0.2)
          
          validation_datagen = ImageDataGenerator(rescale = 1./255)
      
          training_set = train_datagen.flow_from_directory('dataset/training_set',
                                                       target_size = (LocalisationCNN.IMGHEIGHT, LocalisationCNN.IMGWIDTH),
                                                       batch_size = 32,
                                                       class_mode = 'categorical')
          
          validation_set = validation_datagen.flow_from_directory('dataset/validation_set',
                                                   target_size = (LocalisationCNN.IMGHEIGHT, LocalisationCNN.IMGWIDTH),
                                                   batch_size = 32,
                                                   class_mode = 'categorical')
      
          cnn = LocalisationCNN.build_cnn(LocalisationCNN.IMGWIDTH, LocalisationCNN.IMGHEIGHT)
          history = cnn.fit_generator(training_set,
                                   steps_per_epoch = training_set.samples/bs,
                                   epochs = epochs,
                                   validation_data = validation_set,
                                   validation_steps = validation_set.samples/bs)
                  # summarize history for accuracy
          plt.plot(history.history['acc'])
          plt.plot(history.history['val_acc'])
          plt.title('model accuracy')
          plt.ylabel('accuracy')
          plt.xlabel('epoch')
          plt.legend(['train', 'validation'], loc='upper left')
          plt.show()
          # summarize history for loss
          plt.plot(history.history['loss'])
          plt.plot(history.history['val_loss'])
          plt.title('model loss')
          plt.ylabel('loss')
          plt.xlabel('epoch')
          plt.legend(['train', 'validation'], loc='upper left')
          plt.show()
          
          cnn.save('localisation_cnn.h5') #creates a HDF5 file with the trained NN
          
      #Function to classify image on trained CNN    
      def classify_image(self, pepper_image):
        img = pepper_image.resize((self.IMGWIDTH,self.IMGHEIGHT))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        result = self.trained_cnn.predict_classes(img_array)
        return result
        #0=Cantine, 1=Elavators, 2=Exit, 3=Negatives, 4=Stairs, 5=Toilet
        
      #Function for testing the trained CNN  
      def test_cnn(self):
          from sklearn.metrics import confusion_matrix
          self.trained_cnn = load_model('localisation_cnn.h5')
          test_datagen = ImageDataGenerator(rescale = 1./255)
          test_set = test_datagen.flow_from_directory('dataset/test_set',
                                        target_size = (self.IMGHEIGHT, self.IMGWIDTH),
                                        batch_size = 32,
                                        shuffle=False,
                                        class_mode = 'categorical') 
          y_true = None
          y_predicted = None
          is_first_iter = True
          iteration = 1
          images_predicted = 0
          steps = test_set.samples/32
          for X_batch, y_batch in test_set:
              current_batch_size = X_batch.shape[0]
              if (iteration - 1) >= steps:
                    break
              print('Iteration ', iteration)
              y_batch_predicted = np.zeros((current_batch_size, 1))
              for i in range(current_batch_size):
                    images_predicted += 1
                    image_to_predict = X_batch[i].reshape(1, X_batch[i].shape[0], X_batch[i].shape[1], X_batch[i].shape[2])
                    prediction = self.trained_cnn.predict_classes(image_to_predict)
                    y_batch_predicted[i,0] = prediction
                    prediction_class_name = None
                    for key, value in test_set.class_indices.items():
                        if (value == prediction):
                            prediction_class_name = key
                            break
                    print(prediction_class_name)
              if (is_first_iter):
                    y_true = y_batch.argmax(axis=1)
                    y_predicted = y_batch_predicted
                    is_first_iter = False
              else:
                  y_true = np.concatenate((y_true, y_batch.argmax(axis=1)))
                  y_predicted = np.concatenate((y_predicted, y_batch_predicted))
                    
              iteration += 1
              print('Images predicted: ', images_predicted)
          y_predicted = y_predicted.reshape((-1,)).astype(np.int32)
          #print("y_true: ", y_true)
          #print("y_predicted: ", y_predicted)
          print("Class labels: ", test_set.class_indices)
          global confusion_m
          confusion_m = confusion_matrix(y_true, y_predicted)


#LocalisationCNN = LocalisationCNN()
#LocalisationCNN.train_cnn(32, 10)
#LocalisationCNN.test_cnn()
 