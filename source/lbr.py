import tensorflow as tf
import argparse
import numpy as np
from collections import Counter

# Assume snyd.py is correctly converted and contains the necessary TensorFlow classes and functions.
from snyd import Net, Game, calc_args

def lbr(game, roll, us, prune=0, prune_type="zero"):
    # All possible opponent rolls - with multiplicity
    roll_cnt = Counter(game.rolls(1 - us))
    op_rolls = roll_cnt.keys()
    reach_probs = np.array(list(roll_cnt.values()), dtype=np.float32)
    reach_probs /= reach_probs.sum()
    op_privs = [game.make_priv(op_roll, 1 - us) for op_roll in op_rolls]

    def inner(state, reach_probs, likelihood):
        calls = game.get_calls(state)
        cur = len(calls) % 2

        if likelihood < prune:
            if prune_type == "zero":
                return 0
            if prune_type == "upper":
                return 1
            if prune_type == "lower":
                return -1
            if prune_type in ["us", "avg"]:
                our_guess = game.model(tf.convert_to_tensor(game.make_priv(roll, us)), tf.convert_to_tensor(state)).numpy()
            if prune_type in ["them", "avg"]:
                op_guess = sum(prob * game.model(tf.convert_to_tensor(op_priv), tf.convert_to_tensor(state)).numpy()
                               for prob, op_priv in zip(reach_probs, op_privs))
                op_guess = -op_guess
            if prune_type == "us":
                return our_guess
            if prune_type == "them":
                return op_guess
            if prune_type == "avg":
                return (our_guess + op_guess) / 2
            assert False

        if calls and calls[-1] == game.LIE_ACTION:
            prev_call = calls[-2] if len(calls) >= 2 else -1
            res = 0
            for prob, op_roll in zip(reach_probs, op_rolls):
                r1, r2 = (roll, op_roll) if us == 0 else (op_roll, roll)
                correct = game.evaluate_call(r1, r2, prev_call)
                if us == cur:
                    val = 1 if correct else -1
                else:
                    val = -1 if correct else 1
                res += prob * val
            return res

        last_call = calls[-1] if len(calls) >= 1 else -1

        if us == cur:
            best = -1
            for action in range(last_call + 1, game.N_ACTIONS):
                new_state = game.apply_action(state, action)
                val = inner(new_state, reach_probs, likelihood)
                best = max(best, val)
            return best
        else:
            policies = np.vstack([game.policy(tf.convert_to_tensor(op_priv), tf.convert_to_tensor(state), last_call)
                                  for op_priv in op_privs])

            score = 0
            for action in range(last_call + 1, game.N_ACTIONS):
                ai = action - last_call - 1
                pa = np.dot(reach_probs, policies[:, ai])
                if np.isclose(pa, 0.0):
                    continue
                new_reach_probs = (reach_probs * policies[:, ai]) / pa
                new_state = game.apply_action(state, action)
                val = inner(new_state, new_reach_probs, likelihood * pa)
                score += pa * val
            return score

    return inner(game.make_state(), reach_probs, 1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path of model to test")
    parser.add_argument("--prune", type=float, default=0.0, help="Prune nodes with likelihood < prune")
    parser.add_argument("--type", type=str, default="zero", help="What should be used in place of the real value in pruned nodes?")
    args = parser.parse_args()

    checkpoint = tf.keras.models.load_model(args.path)
    train_args = checkpoint.args

    D_PUB, D_PRI, *_ = calc_args(train_args.d1, train_args.d2, train_args.sides, train_args.variant)
    model = Net(D_PRI, D_PUB)
    model.set_weights(checkpoint.get_weights())
    game = Game(model, train_args.d1, train_args.d2, train_args.sides, train_args.variant)

    for player in range(2):
        print(f"Testing exploitability of player {1 - player}")

        total_val = 0
        total_cnt = 0
        for roll, cnt in Counter(game.rolls(player)).items():
            print("Exploiting with roll", roll)
            total_val += cnt * lbr(game, roll, player, args.prune, args.type)
            total_cnt += cnt

        print(total_val / total_cnt)

if __name__ == "__main__":
    main()
