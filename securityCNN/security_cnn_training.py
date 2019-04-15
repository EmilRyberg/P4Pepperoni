from keras.models import Sequential
from keras.models import load_model
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import BatchNormalization
from keras.layers import Activation
from keras.layers import Dense
from keras.layers import Dropout
from keras.preprocessing.image import ImageDataGenerator
from keras import regularizers
from keras.optimizers import Adam
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot as plt
import numpy as np

import tensorflow as tf
from keras.backend import tensorflow_backend
config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
session = tf.Session(config=config)
tensorflow_backend.set_session(session)

classifier = Sequential()
batch_size = 50
image_size = (160, 160)

train_datagen = ImageDataGenerator(rescale=1./255,
                                   rotation_range=40,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True,
                                   vertical_flip=True,
                                   fill_mode='nearest')

validation_datagen = ImageDataGenerator(rescale = 1./255)

test_datagen = ImageDataGenerator(rescale = 1./255)

training_set = train_datagen.flow_from_directory('dataset/training_set',
                                                 target_size = image_size,
                                                 batch_size = batch_size,
                                                 class_mode = 'categorical')

validation_set = validation_datagen.flow_from_directory('dataset/validation_set',
                                            target_size = image_size,
                                            batch_size = batch_size,
                                            class_mode = 'categorical')

test_set = test_datagen.flow_from_directory('dataset/test_set',
                                            target_size = image_size,
                                            batch_size = batch_size,
                                            class_mode = 'categorical')

confusion_m = np.zeros((3,3))

def train_model():
    classifier.add(Conv2D(32, (3, 3), input_shape = (160, 160, 3)))
    classifier.add(Activation('relu'))
    classifier.add(Conv2D(32, (3, 3)))
    classifier.add(Activation('relu'))
    #classifier.add(BatchNormalization())
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(64, (3, 3)))
    classifier.add(Activation('relu'))
    classifier.add(Conv2D(64, (3, 3)))
    classifier.add(Activation('relu'))
    #classifier.add(BatchNormalization())
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(64, (3, 3)))
    classifier.add(Activation('relu'))
    #classifier.add(BatchNormalization())
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
    # Step 3 - Flattening
    classifier.add(Flatten())
    #classifier.add(Dropout(0.25))
    # Step 4 - Full connection
    classifier.add(Dense(units = 512, activation = 'relu')) 
    #classifier.add(Dropout(0.25))
    classifier.add(Dense(units = 512, activation = 'relu')) 
    classifier.add(Dense(units = 512, activation = 'relu')) 
    #classifier.add(Dropout(0.25))
    classifier.add(Dense(units = 4, activation = 'softmax'))
    
    adam_optimizer = Adam(lr=0.001)
    
    # Compiling the CNN
    classifier.compile(optimizer = adam_optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy'])
    classifier.summary()
    
    history = classifier.fit_generator(training_set,
                             steps_per_epoch = training_set.samples/batch_size,
                             epochs = 30,
                             validation_data = validation_set,
                             validation_steps = validation_set.samples/batch_size)
    
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

    score, acc = classifier.evaluate_generator(test_set, steps = test_set.samples/batch_size)
    print('Test accuracy:', acc)
    #classifier.save_weights('training2.h5')
    classifier.save('model7.h5')
    
def view_training_images():
    for X_batch, y_batch in training_set:
        for i in range(0, 8):
            plt.subplot(330 + 1 + i)
            plt.imshow(X_batch[i])
        plt.show()
        break


def test_model(load_model_from_file = False, model_name = None):
    if (load_model_from_file):
        classifier = load_model(model_name)
    y_true = None
    y_predicted = None
    is_first_iter = True
    iteration = 1
    images_predicted = 0
    steps = test_set.samples/batch_size
    for X_batch, y_batch in test_set:
        current_batch_size = X_batch.shape[0]
        if (iteration - 1) >= steps:
            break
        print('Iteration ', iteration)
        y_batch_predicted = np.zeros((current_batch_size, 1))
        for i in range(current_batch_size):
            images_predicted += 1
            image_to_predict = X_batch[i].reshape(1, X_batch[i].shape[0], X_batch[i].shape[1], X_batch[i].shape[2])
            prediction = classifier.predict_classes(image_to_predict)
            y_batch_predicted[i,0] = prediction
            prediction_class_name = None
            true_class_name = None
            for key, value in test_set.class_indices.items():
                if (value == prediction):
                    prediction_class_name = key
                elif (value == y_batch[i].argmax()):
                    true_class_name = key
                    
            if (prediction != y_batch[i].argmax()):
                plt.imshow(X_batch[i])
                plt.title("P: {0}, T: {1}".format(prediction_class_name, true_class_name))
                plt.show()
            #print(prediction_class_name)
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

def main():
    test_model(load_model_from_file = True, model_name = 'model7.h5')
    #train_model()
    
if __name__ == "__main__":
    main()
