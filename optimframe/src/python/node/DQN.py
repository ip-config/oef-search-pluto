from keras.models import Model
from keras.layers import Conv2D, Input, BatchNormalization, GlobalAveragePooling2D, MaxPool2D, Activation, Dense
from keras.optimizers import Adam
import random
import numpy as np


class DQN:

    def __init__(self, batch_size, memory_size, dimensions, name):
        self._memory = []
        self._batch_size = batch_size
        self._memory_size = memory_size
        self._learning_rate = 1e-3
        self._gamma = 0.9
        self._epsilon = 1.0
        self._epsilon_decay = 0.98
        self._epsilon_min = 0.01
        self._action_space = dimensions[-1]
        self._model = self._build_model(*dimensions)
        self._name = name

    def _conv(self, f, kernel, stride=(1, 1)):
        def builder(x):
            y = Conv2D(f, kernel, strides=stride)(x)
            y = Activation('relu')(y)
            y = BatchNormalization()(y)
            return y
        return builder

    def _build_model(self, w, h, c, action_space):
        input_layer = Input((w, h, c))
        x = self._conv(4, (3, 3))(input_layer)
        x = self._conv(4, (3, 3))(x)
        x = MaxPool2D()(x)
        x = self._conv(8, (3, 3))(x)
        x = self._conv(8, (3, 3))(x)
        x = MaxPool2D()(x)
        x = self._conv(16, (3, 3))(x)
        x = self._conv(16, (3, 3))(x)
        x = MaxPool2D()(x)
        x = self._conv(32, (3, 3))(x)
        x = self._conv(32, (3, 3))(x)
        x = MaxPool2D()(x)
        x = self._conv(64, (3, 3))(x)
        x = self._conv(64, (3, 3))(x)
        #x = MaxPool2D()(x)
        #x = self._conv(128, (3, 3))(x)
        #x = self._conv(128, (3, 3))(x)
        #x = MaxPool2D()(x)
        #x = self._conv(256, (3, 3))(x)
        #x = self._conv(256, (3, 3))(x)
        x = GlobalAveragePooling2D()(x)
        x = Dense(action_space, activation=None)(x)
        model = Model(inputs=input_layer, outputs=x)
        model.compile(loss='mse', optimizer=Adam(lr=self._learning_rate))
        model.summary()
        return model

    def remember(self, state, action, reward, next_state):
        self._memory.append((state, action, reward, next_state))
        while len(self._memory) >= self._memory_size:
            self._memory.pop(0)

    def replay(self):
        print("REPLAY {}".format(self._name))
        batch = random.sample(self._memory, self._batch_size)
        for state, action, reward, next_state in batch:
            state_rs = state.reshape((1, *state.shape))
            next_state_rs = next_state.reshape((1, *state.shape))
            target = reward + self._gamma*np.amax(self._model.predict(next_state_rs)[0])
            target_s = self._model.predict(state_rs)
            target_s[0][action] = target
            self._model.fit(state_rs, target_s, epochs=1)
        if self._epsilon > self._epsilon_min:
            self._epsilon *= self._epsilon_decay

    def predict_action(self, state):
        if np.random.random() <= self._epsilon:
            return np.random.randint(0, self._action_space-1)
        pred = self._model.predict(state.reshape((1, *state.shape)))
        return np.argmax(pred[0])
