import random
import numpy as np
import itertools
import argparse
import re
import tensorflow as tf
from snyd import *

# model_path_v1=r"C:\studia\semestr4\biologiczne\ChopinBot\source\model.h5"

# parser = argparse.ArgumentParser()
# parser.add_argument(model_path_v1, type=str, help="Path of model")
args = r"C:\studia\semestr4\biologiczne\ChopinBot\source\model.h5"

# Define the model architecture
train_args = {
    'd1': 3,  # replace with actual value used during training
    'd2': 3,  # replace with actual value used during training
    'sides': 6,  # replace with actual value used during training
    'variant': 'default'  # replace with actual value used during training
}

D_PUB, D_PRI, *_ = calc_args()
model = NetConcat()

# Call the model with dummy data

dummy_data_inputs = np.zeros((1, D_PRI))
dummy_data_pub = np.zeros((1, D_PUB))
model(dummy_data_inputs, dummy_data_pub)


# Load the weights
model.load_weights(args)

class Sieman():
    def play_turn(self,kosci1,kosci2):

        game = Game(model,kosci1,kosci2)


        class Human:
            def get_action(self, state):
                last_call = game.get_last_call(state)
                while True:
                    call = input('Your call [e.g. 24 for 2 fours, or "lie" to call a bluff]: ')
                    if call == "lie":
                        return game.LIE_ACTION
                    elif m := re.match(r"(\d)(\d)", call):
                        n, d = map(int, m.groups())
                        action = (n - 1) * game.SIDES + (d - 1)
                        if action <= last_call:
                            print(f"Can't make that call after {repr_action(last_call)}")
                        elif action >= game.LIE_ACTION:
                            print(f"The largest call you can make is {repr_action(game.LIE_ACTION-1)}")
                        else:
                            return action

            def __repr__(self):
                return "human"

        class Robot:
            def __init__(self, priv):
                self.priv = priv

            def get_action(self, state):
                last_call = game.get_last_call(state)
                return game.sample_action(self.priv, state, last_call, eps=0)

            def __repr__(self):
                return "robot"


        def repr_action(action):
            action = int(action)
            if action == -1:
                return "nothing"
            if action == game.LIE_ACTION:
                return "lie"
            n, d = divmod(action, game.SIDES)
            n, d = n + 1, d + 1
            return f"{n} {d}s"


        while True:
            while (ans := input("Do you want to go first? [y/n/r] ")) not in ["y", "n", "r"]:
                pass

            r1 = random.choice(list(game.rolls(0)))
            r2 = random.choice(list(game.rolls(1)))
            privs = [game.make_priv(r1, 0), game.make_priv(r2, 1)]
            state = game.make_state()

            if ans == "y":
                print(f"> You rolled {r1}!")
                players = [Human(), Robot(privs[1])]
            elif ans == "n":
                print(f"> You rolled {r2}!")
                players = [Robot(privs[0]), Human()]
            elif ans == "r":
                players = [Robot(privs[0]), Robot(privs[1])]

            cur = 0
            while True:
                action = players[cur].get_action(state)
                print()
                print(f"> The {players[cur]} called {repr_action(action)}!")

                if action == game.LIE_ACTION:
                    last_call = game.get_last_call(state)
                    res = game.evaluate_call(r1, r2, last_call)
                    print()
                    print(f"> The rolls were {r1} and {r2}.")
                    if res:
                        print(f"> The call {repr_action(last_call)} was good!")
                        print(f"> The {players[cur]} loses!")
                    else:
                        print(f"> The call {repr_action(last_call)} was a bluff!")
                        print(f"> The {players[cur]} wins!")
                    print()
                    break

                state = game.apply_action(state, action)
                cur = 1 - cur