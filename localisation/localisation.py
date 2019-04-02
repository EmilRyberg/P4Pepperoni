# Importing libraries
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import numpy as np

class LocalisationCNN:
      #Desired image sizes used by ImageDataGenerator under training
      IMGWIDTH = 128
      IMGHEIGHT = 96
      
      # Building the CNN
      def build_cnn(self, ImgWidth, ImgHeight):
          #Initialising the CNN
          cnn = Sequential()
          #First Conv+Pool layer
          cnn.add(Conv2D(32, (3, 3), input_shape = (ImgWidth, ImgHeight, 3), activation = 'relu'))
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
                                         zoom_range = 0.2,
                                         horizontal_flip = True)
          
          validation_datagen = ImageDataGenerator(rescale = 1./255)
      
          training_set = train_datagen.flow_from_directory('dataset/training_set',
                                                       target_size = (LocalisationCNN.IMGWIDTH, LocalisationCNN.IMGHEIGHT),
                                                       batch_size = 32,
                                                       class_mode = 'categorical')
          
          validation_set = validation_datagen.flow_from_directory('dataset/validation_set',
                                                   target_size = (LocalisationCNN.IMGWIDTH, LocalisationCNN.IMGHEIGHT),
                                                   batch_size = 32,
                                                   class_mode = 'categorical')
      
          cnn = LocalisationCNN.build_cnn(LocalisationCNN.IMGWIDTH, LocalisationCNN.IMGHEIGHT)
          cnn.fit_generator(training_set,
                                   steps_per_epoch = training_set.samples/bs,
                                   epochs = epochs,
                                   validation_data = validation_set,
                                   validation_steps = validation_set.samples/bs)
          
          cnn.save('localisation_cnn.h5') #creates a HDF5 file with the trained NN
          
      #Function to classify image on trained CNN    
      def classify_image(self):
          TrainedCnn = load_model('localisation_cnn.h5')
          InputImage = image.load_img('dataset/test_set/Cantine/Cantine.1.jpg', target_size = (LocalisationCNN.IMGWIDTH, LocalisationCNN.IMGHEIGHT))
          InputImage = image.img_to_array(InputImage)
          InputImage = np.expand_dims(InputImage, axis = 0)
          result = TrainedCnn.predict(InputImage)
          return result
        
      #Function for testing the trained CNN  
      def test_cnn(self):
          from sklearn import metrics
          TrainedCnn = load_model('localisation_cnn.h5')
          
          test_datagen = ImageDataGenerator(rescale = 1./255)
          test_set = test_datagen.flow_from_directory('dataset/test_set',
                                        target_size = (LocalisationCNN.IMGWIDTH, LocalisationCNN.IMGHEIGHT),
                                        batch_size = 32,
                                        shuffle=False,
                                        class_mode = 'categorical')
          EpochSteps = np.math.ceil(test_set.samples / 32)

          Predictions = TrainedCnn.predict_generator(test_set, steps=EpochSteps)
          
          # Get most likely class
          PredictedClasses = np.argmax(Predictions, axis=1)
          TrueClasses = test_set.classes
          ClassLabels = list(test_set.class_indices.keys()) 
          
          Report = metrics.classification_report(TrueClasses, PredictedClasses, target_names=ClassLabels)
          print(Report)   
          

LocalisationCNN = LocalisationCNN()
LocalisationCNN.train_cnn(32, 10)
#LocalisationCNN.test_cnn()
 