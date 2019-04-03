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

classifier = Sequential()

def train_model():
    batch_size = 64
    image_size = (128, 128)
    
    train_datagen = ImageDataGenerator(rescale = 1./255,
                                       shear_range = 0.2,
                                       zoom_range = 0.2,
                                       horizontal_flip = True)
    
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
    
    classifier.add(Conv2D(32, (3, 3), input_shape = (128, 128, 3)))
    classifier.add(BatchNormalization())
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(32, (3, 3)))
    classifier.add(BatchNormalization())
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(64, (5, 5)))
    classifier.add(BatchNormalization())
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
    # Step 3 - Flattening
    classifier.add(Flatten())
    
    # Step 4 - Full connection
    classifier.add(Dense(units = 128, activation = 'relu')) 
    #classifier.add(Dropout(0.2))
    classifier.add(Dense(units = 64, activation = 'relu'))
    #classifier.add(Dropout(0.2))
    classifier.add(Dense(units = 64, activation = 'relu'))
    #classifier.add(Dropout(0.2))
    #classifier.add(Dense(units = 64, activation = 'relu'))
    classifier.add(Dense(units = 3, activation = 'softmax'))
    
    # Compiling the CNN
    classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    classifier.summary()
    
    history = classifier.fit_generator(training_set,
                             steps_per_epoch = training_set.samples/batch_size,
                             epochs = 120,
                             validation_data = validation_set,
                             validation_steps = validation_set.samples/batch_size)

    score, acc = classifier.evaluate_generator(test_set, steps = test_set.samples/batch_size)
    print('Test accuracy:', acc)

def main():
    train_model()
    
if __name__ == "__main__":
    main()
