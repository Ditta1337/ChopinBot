from Player import Player

class Game:
    def __init__(self, num_players: int, num_dice: int):
        assert num_players > 0 and num_players < 5,  "Number of _players must be greater than 0 and less than 5"
        assert num_dice > 0 and num_dice < 9, "Number of dice must be greater than 0 and less than 9"

        self._num_players = num_players
        self._players = [Player(i, num_dice) for i in range(num_players)]
        self._curr_player = 0
        self._prev_player = None
        self._turn = 0
        self._prev_bet = None

    def play(self) -> str:
        while self._num_players != 1:
            for player in self._players:
                player.roll()
            while True:
                decision = self._players[self._curr_player].take_turn(self._turn == 0, self._prev_bet)
                if decision[0] == 0: #sprawdzam
                    if self.__sum_dice() < self._prev_bet[0]:
                        self.__take_die(self._prev_player)
                    else: 
                        self.__take_die(self._curr_player)
                    break
                elif decision[0] == -1: #dokładnie
                    if self.__sum_dice() == self._prev_bet[0]:
                        for player_num in range(self._num_players):
                            if player_num != self._curr_player:
                                self.__take_die(player_num)
                    else: 
                        self.__take_die(self._curr_player)
                    break
                else: #kosci
                    self._prev_bet = decision
                
                self._prev_player = self._curr_player
                self._curr_player = (self._curr_player + 1) % self._num_players
                self._turn += 1

        return self._players[0].get_name()
                
    
    def __sum_dice(self) -> bool:
        dice_number = 0
        for player in self._players:
            dice_number += player.get_dice(self._prev_bet[1])

        return dice_number
    
    def __take_die(self, player_num: int) -> None:
        self._turn = 0
        self._prev_bet = None
        self._players[player_num].take()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("Gracz " + self._players[player_num].get_name() + " dobiera kość!\nMa teraz " + str(self._players[player_num].get_curr_dies()) + " kości")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        if self._players[player_num].is_out():
            if player_num <= self._curr_player:
                self._curr_player -= 1
            self._players.pop(player_num)
            self._num_players -= 1
           
        


    
