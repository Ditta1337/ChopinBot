import random
import tensorflow as tf

from snyd import *

model = NetConcat()
game = Game(model)

optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
loss_fn = tf.keras.losses.MeanSquaredError()

@tf.function
def train_step(privs, states, targets):
    with tf.GradientTape() as tape:
        predictions = model(privs, states, training=True)
        loss = loss_fn(targets, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return loss

def play(r1, r2, replay_buffer):
    privs = [game.make_priv(r1, 0), game.make_priv(r2, 1)]

    def play_inner(state):
        cur = game.get_cur(state)
        calls = game.get_calls(state)
        assert cur == len(calls) % 2

        if calls and calls[-1] == game.LIE_ACTION:
            prev_call = calls[-2] if len(calls) >= 2 else -1
            res = 1 if game.evaluate_call(r1, r2, prev_call) else -1
        else:
            last_call = calls[-1] if calls else -1
            action = game.sample_action(privs[cur], state, last_call, 1e-2)
            new_state = game.apply_action(state, action)
            res = -play_inner(new_state)

        replay_buffer.append((privs[cur], state, res))
        replay_buffer.append((privs[1 - cur], state, -res))
        return res

    return play_inner(game.make_state())

def main():
    losses = []
    all_rolls = list(itertools.product(game.rolls(0), game.rolls(1)))
    for t in range(1000):
        replay_buffer = []

        BS = 100  # Number of rolls to include
        for i, (r1, r2) in enumerate(
            all_rolls if len(all_rolls) <= BS else random.sample(all_rolls, BS)
        ):
            play(r1, r2, replay_buffer)
            # print(f"Game {i + 1} of {BS} complete")

        random.shuffle(replay_buffer)
        privs, states, y = zip(*replay_buffer)

        privs = tf.stack(privs)
        states = tf.stack(states)
        y = tf.constant(y, dtype=tf.float32)
        y = tf.reshape(y, (-1, 1))

        loss = train_step(privs, states, y)
        with open("losses_test.txt", "a") as f:
            f.write(f"{t} {loss.numpy()}\n")

        # Compute and print loss
        print(t, loss.numpy())

        model.save_weights("model_test.h5")

if __name__ == "__main__":
    main()
