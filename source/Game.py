from Player import Player


class Game:
    def __init__(self, num_players: int):
        assert num_players > 1 and num_players < 7, "Number of _players must be greater than 0 and less than 5"

        self._num_players = num_players
        self._players = [Player(i) for i in range(num_players)]
        self._curr_player = 0
        self._prev_player = None
        self._turn = 0
        self._prev_bet = None

    def play(self) -> str:
        # round
        while self._num_players != 1:
            for player in self._players:
                player.roll()
            while True:
                # turn
                decision = self._players[self._curr_player].take_turn(self._turn == 0, self._prev_bet)
                if decision[0] == 0:  # sprawdzam
                    if self.__sum_dice() < self._prev_bet[0]:
                        self.__discard_die(self._prev_player)
                    else:
                        self.__discard_die(self._curr_player)
                    break
                elif decision[0] == -1:  # dokładnie
                    if self.__sum_dice() == self._prev_bet[0]:
                        self.__spot_on_handle();
                    else:
                        self.__discard_die(self._curr_player)
                    break
                else:  # kosci
                    self._prev_bet = decision

                self._prev_player = self._curr_player
                self._curr_player = (self._curr_player + 1) % self._num_players
                self._turn += 1

        return self._players[0].get_name()

    def __sum_dice(self) -> bool:
        dice_number = 0
        for player in self._players:
            dice_number += player.get_dice(self._prev_bet[1])
        if self._prev_bet[1] != 1:
            for player in self._players:
                dice_number += player.get_dice(0)
        print("Wyliczyłem ", dice_number, " kostek z ", self._prev_bet[1], " oczkami")
        return dice_number

    def __discard_die(self, player_num: int) -> None:  # dla sprawdzam miałem racje, ziutek odpada
        self._turn = 0
        self._prev_bet = None
        self._players[player_num].discard_die()
        if (self._players[player_num].is_out()):
            print("Gracz ", self._players[player_num].get_name(), " odpada")
            self._num_players -= 1
            self._players.pop(player_num)
            self._curr_player %= self._num_players
        else:
            self.current_player = player_num

    def __spot_on_handle(self) -> None:
        self._turn = 0
        self._prev_bet = None
        updated_players = []
        for i in range(self._num_players):
            if (i != self._curr_player):
                self._players[i].discard_die()
                if (not self._players[i].is_out()):
                    print("Gracz ", self._players[i].get_name(), " odpada")
                    updated_players.append(self._players[i])
                else:
                    self._num_players -= 1
            else:
                updated_players.append(self._players[i])
                self._curr_player = len(updated_players)
        self._curr_player %= self._num_players
        self._players = updated_players
