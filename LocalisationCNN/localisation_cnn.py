# Importing libraries
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import tensorflow as tf

class LocalisationCNN:
    #Desired image sizes used by ImageDataGenerator under training
    IMGWIDTH = 128
    IMGHEIGHT = 96
    trained_cnn = None
    graph = None
     
    #def __init__(self, model_path):
        #self.trained_cnn = load_model(model_path)
        #self.graph = tf.get_default_graph()
      
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
        cnn.add(Dense(256, activation='relu'))
        cnn.add(Dense(256, activation='relu'))
        cnn.add(Dense(256, activation='relu'))
        cnn.add(Dense(units = 6, activation = 'softmax'))
        
        #Compiling the CNN
        cnn.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])  
          
        return cnn
        
    #Fitting the CNN to the training images
    def train_cnn(self, bs, epochs):
        train_datagen = ImageDataGenerator(rescale = 1./255,
                                         shear_range = 0.2,
                                         rotation_range = 5,
                                         zoom_range = 0.2)
          
        validation_datagen = ImageDataGenerator(rescale = 1./255)
      
        training_set = train_datagen.flow_from_directory('dataset/training_set',
                                                       target_size = (self.IMGHEIGHT, self.IMGWIDTH),
                                                       batch_size = 32,
                                                       class_mode = 'categorical')
          
        validation_set = validation_datagen.flow_from_directory('dataset/validation_set',
                                                   target_size = (self.IMGHEIGHT, self.IMGWIDTH),
                                                   batch_size = 32,
                                                   class_mode = 'categorical')
      
        cnn = self.build_cnn(self.IMGWIDTH, self.IMGHEIGHT)
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
          
    #Function for testing the trained CNN  
    def test_cnn(self):
        from sklearn.metrics import confusion_matrix
        self.trained_cnn = load_model('localisation_cnn_shrinkinglayers.h5')
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
               # print(prediction_class_name)
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
        
        class_array = []
        for key, value in test_set.class_indices.items():
            name_with_spaces = ''
            name_index = 0
            for c in key:            
                if c.isupper() and name_index != 0:
                    name_with_spaces += ' ' + c
                else:
                    name_with_spaces += c
                name_index += 1
            class_array.append(name_with_spaces)
            
        self.plot_confusion_matrix(confusion_m, class_array)
        
    def plot_confusion_matrix(self, cm, classes):
        title = 'Localisation confusion matrix'
        # Only use the labels that appear in the data
        #classes = classes[unique_labels(y_true, y_pred)]
        normalize = True
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')
    
        print(cm)
    
        fig, ax = plt.subplots(figsize=(9.6, 6.9))
        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.GnBu)
        ax.figure.colorbar(im, ax=ax)
        # We want to show all ticks...
        ax.set(xticks=np.arange(cm.shape[1]),
               yticks=np.arange(cm.shape[0]),
               # ... and label them with the respective list entries
               xticklabels=classes, yticklabels=classes,
               title=title,
               ylabel='True label',
               xlabel='Predicted label')
    
        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
    
        # Loop over data dimensions and create text annotations.
        fmt = '.3f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")
        fig.tight_layout()
        fig.savefig("confusion_matrix.pdf")
        return ax

localisationCNN = LocalisationCNN()
#localisationCNN.train_cnn(32, 8)
localisationCNN.test_cnn()
 