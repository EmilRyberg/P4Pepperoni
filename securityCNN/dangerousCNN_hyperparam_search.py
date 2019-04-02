# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 11:59:08 2019

@author: Emil
"""

from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import BatchNormalization
from keras.layers import Activation
from keras.layers import Dense
from keras.layers import Dropout
from keras.preprocessing.image import ImageDataGenerator
from keras import regularizers
from hyperopt import Trials, STATUS_OK, tpe
from hyperas import optim
from hyperas.distributions import choice, uniform

best_run = 0
best_model = 0

def data():
    image_size = (128, 128)
    train_datagen = ImageDataGenerator(rescale = 1./255,
                                       shear_range = 0.2,
                                       zoom_range = 0.2,
                                       horizontal_flip = True)
    
    validation_datagen = ImageDataGenerator(rescale = 1./255)
    
    test_datagen = ImageDataGenerator(rescale = 1./255)
    
    training_set = train_datagen.flow_from_directory('dataset/training_set',
                                                     target_size = image_size,
                                                     batch_size = 64,
                                                     class_mode = 'categorical')
    
    validation_set = validation_datagen.flow_from_directory('dataset/validation_set',
                                                target_size = image_size,
                                                batch_size = 64,
                                                class_mode = 'categorical')
    
    test_set = test_datagen.flow_from_directory('dataset/test_set',
                                                target_size = image_size,
                                                batch_size = 64,
                                                class_mode = 'categorical')
    
    return training_set, validation_set

def model(training_set, validation_set):
    # Initialising the CNN
    classifier = Sequential()
    
    convolution_design = {{choice(['one', 'two'])}}
    if convolution_design == 'one':
        classifier.add(Conv2D(16, (3, 3), input_shape = (128, 128, 3)))
        #classifier.add(BatchNormalization())
        classifier.add(Activation('relu'))
        classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
        classifier.add(Conv2D(32, (3, 3)))
        #classifier.add(BatchNormalization())
        classifier.add(Activation('relu'))
        classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
        classifier.add(Conv2D(64, (7, 7)))
        #classifier.add(BatchNormalization())
        classifier.add(Activation('relu'))
        classifier.add(MaxPooling2D(pool_size = (2, 2)))
    elif convolution_design == 'two':
        classifier.add(Conv2D(32, (3, 3), input_shape = (128, 128, 3)))
        #classifier.add(BatchNormalization())
        classifier.add(Activation('relu'))
        classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
        classifier.add(Conv2D(32, (3, 3)))
        #classifier.add(BatchNormalization())
        classifier.add(Activation('relu'))
        classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
        classifier.add(Conv2D(64, (5, 5)))
        #classifier.add(BatchNormalization())
        classifier.add(Activation('relu'))
        classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
        last_layer = {{choice(['yes', 'no'])}}
        if last_layer == 'yes':
            classifier.add(Conv2D(64, (7, 7)))
            #classifier.add(BatchNormalization())
            classifier.add(Activation('relu'))
            classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    
    # Step 3 - Flattening
    classifier.add(Flatten())
    
    # Step 4 - Full connection
    classifier.add(Dense(units = {{choice([64, 128, 256, 512, 1024])}}, activation = 'relu')) 
    classifier.add(Dropout({{uniform(0, 1)}}))
    dense_layers = {{choice(['one', 'two'])}}
    if dense_layers == 'two':
        classifier.add(Dense(units = {{choice([64, 128, 256])}}, activation = 'relu'))
        classifier.add(Dropout({{uniform(0, 1)}}))
    #classifier.add(Dense(units = 64, activation = 'relu'))
    classifier.add(Dense(units = 3, activation = 'softmax'))
    
    # Compiling the CNN
    classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    
    #classifier.summary()
    
    history = classifier.fit_generator(training_set,
                             steps_per_epoch = 70,
                             epochs = 1,
                             validation_data = validation_set,
                             validation_steps = 70)

    score, acc = classifier.evaluate_generator(validation_set, steps = 70)
    print('Test accuracy:', acc)
    return {'loss': -acc, 'status': STATUS_OK, 'model': classifier}

def main():
    training_set, validation_set = data()
    global best_run
    global best_model
    best_run, best_model = optim.minimize(model=model,
                                      data=data,
                                      algo=tpe.suggest,
                                      max_evals=1,
                                      trials=Trials())

if __name__ == "__main__":
    main()
