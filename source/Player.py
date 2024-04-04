import random

class Player:
    def __init__(self, id: int, num_dice: int) -> None:
        self._id = id
        self._name = self.__get_player_name()
        self._dice_arr = [0 for _ in range(6)]
        self._curr_dice = 1
        self._dice_to_take = num_dice - 1

    def roll(self) -> None:
        self._dice_arr = [0 for _ in range(6)]
        for i in range(self._curr_dice):
            self._dice_arr[random.randint(0, 5)] += 1

    def take(self) -> None:
        self._curr_dice += 1
        self._dice_to_take -= 1
        
    def is_out(self) -> bool:
        return self._dice_to_take == -1
    
    def get_dice(self, dice: int) -> int:
        return self._dice_arr[dice - 1]
    
    def take_turn(self, is_first: bool, prev_bet: tuple[int, int]) -> tuple[int, int]:
        try:
            while True:
                print(f"{self._name} rzut: {self._dice_arr}\n")
                first_input, success = self.__input_to_int("-1: dokładnie\n0: sprawdzam\n>0: ilość kości \n")
                if not success or first_input < -1 or (first_input < 1 and is_first):
                    print("niepoprawny input!")
                    continue
                if first_input < 1:
                    return (first_input, -1)
                second_input, success = self.__input_to_int("podaj ilość oczek: \n")
                if second_input < 1 or second_input > 6:
                    print("niepoprawny input!")
                    continue
                potetnial_bet = (first_input, second_input)
                if self.__check_bet_val_idity(potetnial_bet, prev_bet):
                    return potetnial_bet
                else:
                    print("niepoprawny bet!\n")
        except KeyboardInterrupt:
            print("przerwano grę!\n")
            exit(0)

    def get_curr_dies(self) -> int:
        return self._curr_dice

    def get_name(self) -> str:
        return self._name

    def __check_bet_val_idity(self, curr_bet: tuple[int, int], prev_bet: tuple[int, int]) -> bool:
        if prev_bet == None:
            return True
        if curr_bet[1] == 1 and prev_bet[1] != 1:
            return curr_bet[0] > prev_bet[0] // 2
        elif curr_bet[1] == 1 and prev_bet[1] == 1:
            return curr_bet[0] > prev_bet[0]
        elif curr_bet[1] != 1 and prev_bet[1] == 1:
            return curr_bet[0] > prev_bet[0] * 2
        else:
            return curr_bet[0] > prev_bet[0] or curr_bet[1] > prev_bet[1]



    def __input_to_int(self, prompt: str) -> tuple[int, bool]:
        try:
            return (int(input(prompt)), True)
        except:
            return (-1, False)

        
    def __get_player_name(self) -> str:
        return input(f"Podaj imie gracza {self._id}: ")
