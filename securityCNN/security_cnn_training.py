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
from matplotlib import pyplot

classifier = Sequential()
batch_size = 32
image_size = (224, 224)

train_datagen = ImageDataGenerator(rescale=1./255,
                                   rotation_range=40,
                                   width_shift_range=0.2,
                                   height_shift_range=0.2,
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

def train_model():
    classifier.add(Conv2D(16, (3, 3), input_shape = (224, 224, 3)))
    #classifier.add(BatchNormalization())
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(16, (3, 3)))
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
        
    # Step 3 - Flattening
    classifier.add(Flatten())
    
    # Step 4 - Full connection
    classifier.add(Dense(units = 2056, activation = 'relu')) 
    #classifier.add(Dropout(0.2))
    classifier.add(Dense(units = 2056, activation = 'relu')) 
    #classifier.add(Dropout(0.2))
    #classifier.add(Dense(units = 64, activation = 'relu'))
    #classifier.add(Dropout(0.2))
    #classifier.add(Dense(units = 64, activation = 'relu'))
    classifier.add(Dense(units = 3, activation = 'softmax'))
    
    # Compiling the CNN
    classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    classifier.summary()
    
    history = classifier.fit_generator(training_set,
                             steps_per_epoch = training_set.samples/batch_size,
                             epochs = 60,
                             validation_data = validation_set,
                             validation_steps = validation_set.samples/batch_size)

    score, acc = classifier.evaluate_generator(test_set, steps = test_set.samples/batch_size)
    print('Test accuracy:', acc)
    classifier.save_weights('training.h5')
    
def view_training_images():
    for X_batch, y_batch in training_set:
        for i in range(0, 8):
            pyplot.subplot(330 + 1 + i)
            pyplot.imshow(X_batch[i])
        pyplot.show()
        break


def classify_test_set():
    for X_batch, y_batch in test_set:
        for i in range(X_batch.shape[0]):
            #pyplot.subplot(330 + 1 + i)
            #pyplot.imshow(X_batch[i])
            image_to_predict = X_batch[i].reshape(1, X_batch[i].shape[0], X_batch[i].shape[1], X_batch[i].shape[2])
            prediction = classifier.predict_classes(image_to_predict)
            prediction_class_name = None
            for key, value in test_set.class_indices.items():
                if (value == prediction):
                    prediction_class_name = key
                    break
            print(prediction_class_name)
            # show the plot
        #pyplot.show()
        #break

def main():
    train_model()
    
if __name__ == "__main__":
    main()
