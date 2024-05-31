import random
import itertools
import numpy as np
import tensorflow as tf
from collections import Counter

class NetConcat(tf.keras.Model):
    def __init__(self):
        super(NetConcat, self).__init__()
        hiddens = [500, 400, 300, 200, 100]
        self.layers_ = [tf.keras.layers.Dense(units, activation='relu') for units in hiddens]
        self.output_layer = tf.keras.layers.Dense(1, activation='tanh')

    def call(self, priv, pub):
        x = tf.concat([priv, pub], axis=-1)
        for layer in self.layers_:
            x = layer(x)
        return self.output_layer(x)

def calc_args():
    D1 = D2 = 5
    sides = 6
    variant = "joker"
    
    D_PUB = (D1 + D2) * sides
    if variant == "stairs":
        D_PUB = 2 * (D1 + D2) * sides

    LIE_ACTION = D_PUB
    D_PUB += 1

    N_ACTIONS = D_PUB

    CUR_INDEX = D_PUB
    D_PUB += 1

    D_PUB_PER_PLAYER = D_PUB
    D_PUB *= 2

    D_PRI = max(D1, D2) * sides
    PRI_INDEX = D_PRI
    D_PRI += 2

    return D_PUB, D_PRI, N_ACTIONS, LIE_ACTION, CUR_INDEX, PRI_INDEX, D_PUB_PER_PLAYER

class Game:
    def __init__(self, model):
        self.model = model
        self.D1 = self.D2 = 5
        self.SIDES = 6
        self.VARIANT = "joker"

        (self.D_PUB, self.D_PRI, self.N_ACTIONS, self.LIE_ACTION, self.CUR_INDEX,
         self.PRI_INDEX, self.D_PUB_PER_PLAYER) = calc_args()

    def make_regrets(self, priv, state, last_call):
        if priv[self.PRI_INDEX] != state[self.CUR_INDEX]:
            print("Warning: Regrets are not with respect to current player")

        n_actions = self.N_ACTIONS - last_call - 1
        
        # Ensure state is 2D by adding a batch dimension
        state = tf.expand_dims(state, axis=0)

        batch = tf.tile(state, [n_actions + 1, 1])

        for i in range(n_actions):
            batch = tf.tensor_scatter_nd_update(batch, [[i + 1]], [self._apply_action(batch[i + 1], i + last_call + 1)])

        # Ensure priv is 2D by adding a batch dimension
        priv = tf.expand_dims(priv, axis=0)
        priv_batch = tf.tile(priv, [n_actions + 1, 1])

        v = self.model(priv_batch, batch)
        vs = v[1:]
        return [max(vi - v[0], 0) for vi in vs]

    def evaluate_call(self, r1, r2, last_call):
        if last_call == -1:
            return True

        n, d = divmod(last_call, self.SIDES)
        n, d = n + 1, d + 1

        cnt = Counter(r1 + r2)
        if self.VARIANT == "joker":
            actual = cnt[d] + cnt[1] if d != 1 else cnt[d]
        return actual >= n

    def policy(self, priv, state, last_call, eps=0):
        regrets = self.make_regrets(priv, state, last_call)
        for i in range(len(regrets)):
            regrets[i] += eps
        
        if sum(regrets) <= 0:
            pi = [1 / len(regrets)] * len(regrets)
        else:
            s = sum(regrets)
            pi = [r / s for r in regrets]

        # Convert list of tensors or floats to a flat numpy array
        pi = np.array([p if isinstance(p, float) else p.numpy()[0] for p in pi])

        # Debugging print to ensure dimensions are correct
        # print(f"Policy probabilities (pi): {pi}")
        # print(f"Shape of pi: {np.shape(pi)}")

        return pi



    def sample_action(self, priv, state, last_call, eps):
        pi = self.policy(priv, state, last_call, eps)
        action = np.random.choice(len(pi), p=pi)
        return action + last_call + 1

    def apply_action(self, state, action):
        new_state = tf.identity(state)
        new_state = self._apply_action(new_state, action)
        return new_state

    def _apply_action(self, state, action):
        cur = self.get_cur(state)
        state = tf.tensor_scatter_nd_update(state, [[action + cur * self.D_PUB_PER_PLAYER]], [1])
        state = tf.tensor_scatter_nd_update(state, [[self.CUR_INDEX + cur * self.D_PUB_PER_PLAYER]], [0])
        state = tf.tensor_scatter_nd_update(state, [[self.CUR_INDEX + (1 - cur) * self.D_PUB_PER_PLAYER]], [1])
        return state

    def make_priv(self, roll, player):
        priv = tf.zeros(self.D_PRI)
        priv = tf.tensor_scatter_nd_update(priv, [[self.PRI_INDEX + player]], [1.0])
        cnt = Counter(roll)
        for face, c in cnt.items():
            for i in range(c):
                priv = tf.tensor_scatter_nd_update(priv, [[(face - 1) * max(self.D1, self.D2) + i]], [1.0])
        return priv

    def make_state(self):
        state = tf.zeros(self.D_PUB)
        state = tf.tensor_scatter_nd_update(state, [[self.CUR_INDEX]], [1.0])
        return state

    def get_cur(self, state):
        return 1 - int(state[self.CUR_INDEX])

    def rolls(self, player):
        n_faces = self.D1 if player == 0 else self.D2
        return [tuple(sorted(r)) for r in itertools.product(range(1, self.SIDES + 1), repeat=n_faces)]

    def get_calls(self, state):
        merged = state[:self.CUR_INDEX] + state[self.D_PUB_PER_PLAYER:self.D_PUB_PER_PLAYER + self.CUR_INDEX]
        return tf.where(merged == 1).numpy().flatten().tolist()

    def get_last_call(self, state):
        ids = self.get_calls(state)
        if not ids:
            return -1
        return int(ids[-1])
