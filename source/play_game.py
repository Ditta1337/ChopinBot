from Game import Game

def play_game(num_players: int, num_dice: int) -> None:
    game = Game(num_players, num_dice)
    return game.play()

if __name__ == "__main__":
    while True:
        try:
            num_players = int(input("Podaj liczbę graczy: "))
            num_dice = int(input("Podaj liczbę kości: "))
            if num_players < 2 or num_dice < 1:
                raise ValueError
            break
        except ValueError:
            print("niepoprawne dane!")
            continue
        except KeyboardInterrupt:
            print("przerwano grę!")
            exit(0)
    print(f"wygrywa: {play_game(num_players, num_dice)}")