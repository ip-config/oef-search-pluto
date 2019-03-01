from keras.models import Model
from keras.layers import Conv2D, Input, BatchNormalization, GlobalAveragePooling2D, MaxPool2D, Activation, Dense
from keras.optimizers import Adam
import random
import numpy as np


class Memory:
    def __init__(self, max_size):
        self._max_size = max_size
        self._state_store = None
        self._action_store = None
        self._reward_store = None
        self._next_state_store = None
        self._start = 0
        self._end = 0

    def _init(self, sshape):
        self._state_store = np.zeros((self._max_size, *sshape), dtype=bool)
        self._next_state_store = np.zeros_like(self._state_store)
        self._action_store = np.zeros((self._max_size, 1), dtype=np.int)
        self._reward_store = np.zeros((self._max_size, 1), dtype=np.double)
        self._start = 0
        self._end = 0

    def push(self, state, action, reward, next_state):
        if self._state_store is None:
            self._init(state.shape)
        i = self._end
        self._state_store[i, :, :, :] = state
        self._next_state_store[i, :, :, :] = next_state
        self._action_store[i] = action
        self._reward_store[i] = reward
        self._end = (self._end+1) % self._max_size
        if self._start == self._end:
            self._start = (self._start + 1) % self._max_size

    def sample(self, batch_size):
        if self._start == 0:
            if self._end < batch_size:
                return None
            else:
                sample = np.random.choice(self._end, batch_size, replace=False)
        else:
            sample = np.random.choice(self._max_size, batch_size, replace=False)
        return self._state_store[sample, :, :, :], self._action_store[sample, :], self._reward_store[sample, :], self._next_state_store[sample, :, :, :]


class DQN:

    def __init__(self, batch_size, memory_size, dimensions, name):
        self._memory = Memory(memory_size)
        self._batch_size = batch_size
        self._learning_rate = 1e-3
        self._gamma = 0.9
        self._epsilon = 1.0
        self._epsilon_decay = 0.95
        self._epsilon_min = 0.01
        self._tau = 0.125
        self._action_space = dimensions[-1]
        self._q_network = self._build_model(*dimensions)
        self._target_network = self._build_model(*dimensions)
        self._name = name
        self._loss = []

    def _conv(self, f, kernel, strides=(1, 1), padding="same"):
        def builder(x):
            y = Conv2D(f, kernel, padding=padding, strides=strides)(x)
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
        x = MaxPool2D()(x)
        x = self._conv(128, (3, 3))(x)
        x = self._conv(128, (3, 3))(x)
        x = GlobalAveragePooling2D()(x)
        x = Dense(action_space, activation=None)(x)
        model = Model(inputs=input_layer, outputs=x)
        model.compile(loss='mse', optimizer=Adam(lr=self._learning_rate))
        model.summary()
        return model

    def remember(self, state, action, reward, next_state):
        self._memory.push(state, action, reward, next_state)

    def replay(self, episode):
        print("REPLAY {}, episode {}".format(self._name, episode))
        mem = self._memory.sample(self._batch_size)
        if mem is None:
            return
        state, action, reward, next_state = mem

        future_q = self._target_network.predict(next_state)
        target = reward + self._gamma*np.amax(future_q, axis=1, keepdims=True)

        y = self._q_network.predict(state)
        y[np.arange(y.shape[0]), action.reshape((-1))] = target.reshape((-1))

        history = self._q_network.fit(state, y, epochs=1)

        self._loss.append(history.history["loss"][0])
        if self._epsilon > self._epsilon_min:
            self._epsilon *= self._epsilon_decay

    def trainTarget(self):
        weights = self._q_network.get_weights()
        target_weights = self._target_network.get_weights()
        for i in range(len(weights)):
            target_weights[i] = (1-self._tau)*target_weights[i] + self._tau*weights[i]
        self._target_network.set_weights(target_weights)

    def getLoss(self):
        return self._loss

    def predict_action(self, state):
        if np.random.random() <= self._epsilon:
            return np.random.randint(0, self._action_space)
        pred = self._q_network.predict(state.reshape((1, *state.shape)))
        print(self._name, ": ", np.argmax(pred[0]), "     ", pred[0])
        return np.argmax(pred[0])
