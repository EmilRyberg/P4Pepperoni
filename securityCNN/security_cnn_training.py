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
from keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot as plt
import numpy as np

import tensorflow as tf
from keras.backend import tensorflow_backend
config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
session = tf.Session(config=config)
tensorflow_backend.set_session(session)

classifier = Sequential()
batch_size = 48
image_size = (200, 200)
model_checkpoint_folder = 'model25_checkpoints'

train_datagen = ImageDataGenerator(rescale=1./255,
                                   rotation_range=60,
                                   shear_range=0.2,
                                   zoom_range=0.25,
                                   #horizontal_flip=True,
                                   fill_mode='nearest',
                                   width_shift_range=0.25,
                                   height_shift_range=0.25)

validation_datagen = ImageDataGenerator(rescale = 1./255)

test_datagen = ImageDataGenerator(rescale = 1./255)

training_set = train_datagen.flow_from_directory('dataset/training_set',
                                                 target_size = image_size,
                                                 batch_size = batch_size,
                                                 class_mode = 'categorical')
                                                 #save_to_dir = 'dataset/training_set_generated')

validation_set = validation_datagen.flow_from_directory('dataset/validation_set',
                                            target_size = image_size,
                                            batch_size = batch_size,
                                            class_mode = 'categorical')

test_set = test_datagen.flow_from_directory('dataset/test_set',
                                            target_size = image_size,
                                            batch_size = batch_size,
                                            class_mode = 'categorical')

confusion_m = None #Will contain the confusion matrix if test_model() is run (is global to be inspectable in editors)

def train_model():
    classifier.add(Conv2D(32, (3, 3), input_shape = (200, 200, 3)))
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(64, (3, 3)))
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(64, (3, 3)))
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    
    classifier.add(Conv2D(128, (3, 3)))
    classifier.add(Activation('relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
        
    classifier.add(Flatten())
    classifier.add(Dropout(0.1))
    
    classifier.add(Dense(units = 1024))
    classifier.add(Activation('relu'))
    classifier.add(Dropout(0.1))
    classifier.add(Dense(units = 1024)) 
    classifier.add(Activation('relu'))
    classifier.add(Dropout(0.1))
    classifier.add(Dense(units = 10, activation = 'softmax'))
    
    adam_optimizer = Adam(lr=0.001)
    
    classifier.compile(optimizer = adam_optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy'])
    classifier.summary()
    
    checkpoint_callback = ModelCheckpoint(model_checkpoint_folder + '/model.{epoch:02d}-{val_acc:.4f}.hdf5', monitor='val_acc', verbose=1, period=1, save_best_only=True)
    #early_stopping_callback = EarlyStopping(monitor='val_loss', min_delta=0.005, patience=8, verbose=1, restore_best_weights=True)
    callbacks = [checkpoint_callback]
    
    history = classifier.fit_generator(training_set,
                             steps_per_epoch = training_set.samples/batch_size,
                             epochs = 80,
                             validation_data = validation_set,
                             validation_steps = validation_set.samples/batch_size,
                             callbacks = callbacks)
    
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.savefig(model_checkpoint_folder + '/accuracy_history.png')
    plt.show()
    
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.savefig(model_checkpoint_folder + '/loss_history.png')
    plt.show()

    score, acc = classifier.evaluate_generator(test_set, steps = test_set.samples/batch_size)
    print('Test accuracy:', acc)
    
def view_training_images():
    for X_batch, y_batch in training_set:
        for i in range(0, 8):
            plt.subplot(330 + 1 + i)
            plt.imshow(X_batch[i])
        plt.show()
        break


def test_model(load_model_from_file = False, model_name = None, show_images = False):
    if (load_model_from_file):
        classifier = load_model(model_name)
    y_true = None
    y_predicted = None
    is_first_iter = True
    iteration = 1
    images_predicted = 0
    incorrect_predictions = 0
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
                    
            if (prediction != y_batch[i].argmax() and show_images):
                plt.imshow(X_batch[i])
                plt.title("P: {0}, T: {1}".format(prediction_class_name, true_class_name))
                plt.show()
                incorrect_predictions += 1
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
    accuracy = 1. - (incorrect_predictions / images_predicted)
    print ('Class labels: ', test_set.class_indices)
    print ('Test accuracy: {0} ({1}/{2})'.format(accuracy, incorrect_predictions, images_predicted))
    
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
    
    global confusion_m
    confusion_m = confusion_matrix(y_true, y_predicted)
    plot_confusion_matrix(confusion_m, class_array)

def plot_confusion_matrix(cm, classes):
    title = 'Object Detection confusion matrix'
    # Only use the labels that appear in the data
    #classes = classes[unique_labels(y_true, y_pred)]
    normalize = True
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots(figsize=(12.8, 9.2))
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

def main():
	#Uncomment either function to test or train model
    test_model(load_model_from_file = True, model_name = 'model21_checkpoints/model.73-0.93.hdf5')
    #train_model()
    
if __name__ == "__main__":
    main()
