from __future__ import print_function

from glob import glob

import keras
from keras.callbacks import ModelCheckpoint
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dense, Dropout, Flatten
from keras.models import Sequential

import utils
from data import get_mnist_data, num_classes, input_shape
import keract

# What this script does:
# - define the model
# - if no checkpoints are detected:
#   - train the model
#   - save the best model in checkpoints/
# - load the model from the best checkpoint
# - read the activations

if __name__ == '__main__':

    checkpoints = glob('examples/checkpoints/*.h5')
    # pip3 install natsort
    from natsort import natsorted

    from keras.models import load_model

    if len(checkpoints) > 0:

        checkpoints = natsorted(checkpoints)
        assert len(checkpoints) != 0, 'No checkpoints found.'
        checkpoint_file = checkpoints[-1]
        print('Loading [{}]'.format(checkpoint_file))
        model = load_model(checkpoint_file)

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        print(model.summary())

        x_train, y_train, x_test, y_test = get_mnist_data()

        # checking that the accuracy is the same as before 99% at the first epoch.
        # test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0, batch_size=128)
        # print('')
        # assert test_acc > 0.98

        utils.print_names_and_shapes(keract.get_activations(model, x_test[0:200]))  # with 200 samples.

        keract.get_gradients_of_trainable_weights(model, x_train[0:10], y_train[0:10])
        keract.get_gradients_of_activations(model, x_train[0:10], y_train[0:10])

        a = keract.get_activations(model, x_test[0:1])  # with just one sample.
        keract.display_activations(a)

        # import numpy as np
        # import matplotlib.pyplot as plt
        # plt.imshow(np.squeeze(x_test[0:1]), interpolation='None', cmap='gray')
    else:
        x_train, y_train, x_test, y_test = get_mnist_data()

        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3),
                         activation='relu',
                         input_shape=input_shape))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes, activation='softmax'))

        model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])

        import shutil
        import os

        # delete folder and its content and creates a new one.
        try:
            shutil.rmtree('checkpoints')
        except:
            pass
        os.mkdir('checkpoints')

        checkpoint = ModelCheckpoint(monitor='val_acc',
                                     filepath='checkpoints/model_{epoch:02d}_{val_acc:.3f}.h5',
                                     save_best_only=True)

        model.fit(x_train, y_train,
                  batch_size=128,
                  epochs=12,
                  verbose=1,
                  validation_data=(x_test, y_test),
                  callbacks=[checkpoint])

        score = model.evaluate(x_test, y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])
