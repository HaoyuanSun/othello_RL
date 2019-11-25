from final_project.othello_env import OthelloGame
import tensorflow as tf
import numpy as np
from collections import deque
from tensorflow.keras import layers
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.initializers import RandomUniform
import random
from time import process_time
import matplotlib.pyplot as plt


class OthelloAgent:
    def __init__(self):
        self.state_size = 64
        self.action_size = 64
        self.tile = 'X'
        self.memory = deque(maxlen=2000)
        self.gamma = 1.0  # episodic --> undiscounted
        self.epsilon = .20
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.learning_rate = 0.01
        self.model = self.build_model()

    def build_model(self):
        # Feed-forward NN
        model = tf.keras.Sequential()
        init = RandomUniform(minval=-0.5, maxval=0.5)
        model.add(layers.Dense(50, input_dim=self.state_size, activation='sigmoid', kernel_initializer=init))
        model.add(layers.Dense(64, activation='sigmoid'))
        model.compile(loss='mse', optimizer=SGD(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def get_action(self, state):
        valid_actions = game.board.get_valid_moves(self.tile)
        if np.random.rand() <= self.epsilon:
            random.shuffle(valid_actions)
            return valid_actions[0]
        else:
            # Take an action based on the Q function
            all_values = self.model.predict(state)
            # return the VALID action with the highest network value
            # use an action_grid that can be indexed by [x, y]
            action_grid = np.reshape(all_values[0], newshape=(8,8))
            q_values = [action_grid[v[0], v[1]] for v in valid_actions]
            return valid_actions[np.argmax(q_values)]

    def replay(self, batch_size):
        """
        Perform backpropogation using stochastic gradient descent.
        Only want to update the state-action pair that is selected (the target for all
                 other actions are set to the NN estimate so that the estimate is zero)
        """
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                         np.amax(self.model.predict(next_state)[0])
            target_NN = self.model.predict(state)
            target_NN[0][action] = target   # only this Q val will be updated
            self.model.fit(state, target_NN, epochs=1, verbose=0)
        # optional epsilon decay feature
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    storing = False
    # initialize agent and environment
    agent = OthelloAgent()
    game = OthelloGame(interactive=False, show_steps=False)

    # FILENAME CONVENTION
    #      'saves/NN-type_opponent_num-episodes'
    if storing:
        save_filename = 'final_project/saves/basic-sequential_rand_2000_2'
        load_filename = 'final_project/saves/basic-sequential_rand_2000'
        agent.load(load_filename + ".h5")

    terminal = False
    batch_size = 32
    episodes = 2000
    avg_result = 0
    results_over_time = np.zeros(episodes)

    # time it
    t_start = process_time()
    for e in range(episodes):
        game.reset()
        game.start()
        state = game.get_state()  # 8x8 numpy array
        state = np.reshape(state, [1, 64])   # 1x64 vector
        help_count = 0

        for move in range(100):   # max amount of moves in an episode
            action = agent.get_action(state)
            reward, next_state, terminal = game.step(action)
            next_state = np.reshape(next_state, [1, 64])
            agent.remember(state, action, reward, next_state, terminal)
            state = next_state
            if terminal:
                # terminal reward is 0 for loss, 0.5 for tie, 1 for win
                # use this as an indexing code to get the result
                outcomes = ['Loss', 'Tie', 'Win']
                result = outcomes[int(reward*2)]
                if result == 'Win':
                    n = 1
                else:
                    n = 0
                avg_result += (1/(e+1))*(n - avg_result)
                results_over_time[e] = avg_result
                print("episode {}: {} moves ({} of which needed help), Result: {}, e: {:.2}"
                      .format(e, move, help_count, result, agent.epsilon))
                print("Average win/loss ratio: ", avg_result)
                break
            # Question - maybe only update every batch_size moves
            #       (instead of every move after batch_size)?
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)

        if e % 100 == 0 and e > 0 and storing:
            # save name as 'saves/model-type_training-opponent_num-episodes.h5'
            agent.save(save_filename + ".h5")

    # present the timed results
    t_stop = process_time()
    print('Runtime: {}.'.format(t_stop-t_start))

    # create and save a figure
    if storing:
        t = [i for i in range(episodes)]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, results_over_time)
        ax.set_xlabel("Episode")
        ax.set_title("Percent Wins During Training")
        plt.savefig(save_filename + '.png')
        np.save(save_filename + '.npy', results_over_time)