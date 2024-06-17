import pygame
from sys import exit
from .Button import Button
from .TextInput import TextInput
from model import *
import re
class UI:
    screen_width = 800
    screen_height = 600
    __images = []
    __dice_image_distance = 10
    __robot_image = 0
    __robot = 0
    __to_display = ""
    __human_dice = []
    __robot_dice = []
    def initialize(self):

        args = "source/model.h5"

        train_args = {
            'd1': 3,
            'd2': 3,
            'sides': 6,
            'variant': 'default'
        }

        D_PUB, D_PRI, *_ = calc_args()
        model = NetConcat()

        dummy_data_inputs = np.zeros((1, D_PRI))
        dummy_data_pub = np.zeros((1, D_PUB))
        model(dummy_data_inputs, dummy_data_pub)
        model.load_weights(args)
        self.__game = Game(model)

        self.r1 = random.choice(list(self.__game.rolls(0)))
        self.r2 = random.choice(list(self.__game.rolls(1)))
        self.__privs = [self.__game.make_priv(self.r1, 0), self.__game.make_priv(self.r2, 1)]
        self.__state = self.__game.make_state()

        pygame.init()
        pygame.font.init()
        self.__screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("ChopinBot")
        clock = pygame.time.Clock()
        self.__check_button = Button(self.screen_width / 4 * 3, self.screen_height / 8 * 7, 100, 50, "check")
        self.__bet_button = Button(self.screen_width / 4, self.screen_height / 8 * 7, 100, 50, "bet")
        self.__continue_button = Button(self.screen_width / 4, self.screen_height / 8 * 7, 150, 50, "continue")
        self.__text_input = TextInput(self.screen_width / 4 * 2, self.screen_height / 8 * 7, 100, 50)

        self.__robot_starts_button = Button(self.screen_width / 2, self.screen_height / 4, 200, 50, "Robot starts")
        self.__human_starts_button = Button(self.screen_width / 2, self.screen_height / 4 * 3, 200, 50, "You start")

        self.__surface = pygame.Surface((self.screen_width, self.screen_height))
        self.__surface.fill('Dark Green')
        self.__load_images()

        self.__choose_start_screen = True
        self.__play_screen = False
        self.__end_screen = False

        while True:
            self.__screen.blit(self.__surface, (0, 0))
            self.__surface.fill('Dark Green')
            self.__event_handler()


            if self.__choose_start_screen:
                self.__human_starts_button.update(pygame.mouse.get_pos())
                self.__robot_starts_button.update(pygame.mouse.get_pos())

                self.__human_starts_button.draw(self.__surface, self.__screen)
                self.__robot_starts_button.draw(self.__surface, self.__screen)

            if self.__play_screen:
                self.__check_button.update(pygame.mouse.get_pos())
                self.__bet_button.update(pygame.mouse.get_pos())

                self.__check_button.draw(self.__surface, self.__screen)
                self.__bet_button.draw(self.__surface, self.__screen)
                self.__text_input.draw(self.__surface, self.__screen)

                self.display_on_the_middle()


                self.__draw_human(self.__human_dice)
                self.__draw_robot(self.__robot_dice, False)

            if self.__end_screen:
                self.__draw_human(self.__human_dice)
                self.__draw_robot(self.__robot_dice, True)
                self.display_on_the_middle()
                self.__continue_button.update(pygame.mouse.get_pos())
                self.__continue_button.draw(self.__surface, self.__screen)


            pygame.display.update()
            clock.tick(30)

    def __event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.__play_screen:
                    if(self.__bet_button.mouse_is_above()):
                        #human move
                        valid_move = False
                        last_call = self.__game.get_last_call(self.__state)
                        call = self.__text_input.get_text()
                        if m := re.match(r"(\d)(\d)", call):
                            n, d = map(int, m.groups())
                            action = (n - 1) * self.__game.SIDES + (d - 1)
                            if action > last_call and action < self.__game.LIE_ACTION:
                                valid_move = True
                                self.__state = self.__game.apply_action(self.__state, action)
                        self.__text_input.clear()
                        #robot move
                        if valid_move:
                            action = self.__robot.get_action(self.__state)
                            self.__to_display = f"Robot called {self.repr_action(action)}! "
                            if action == self.__game.LIE_ACTION:
                                self.__end_screen = True
                                self.__play_screen = False
                                last_call = self.__game.get_last_call(self.__state)
                                res = self.__game.evaluate_call(self.r1, self.r2, last_call)
                                if res:
                                    self.__to_display += f"The call {self.repr_action(last_call)} was good! "
                                    self.__to_display += f"Robot loses!"
                                else:
                                    self.__to_display += f"The call {self.repr_action(last_call)} was a bluff! "
                                    self.__to_display += f"The Robot wins!"
                            else:
                                self.__state = self.__game.apply_action(self.__state, action)
                    elif(self.__check_button.mouse_is_above()):
                        self.__end_screen = True
                        self.__play_screen = False
                        action = self.__game.LIE_ACTION
                        last_call = self.__game.get_last_call(self.__state)
                        res = self.__game.evaluate_call(self.r1, self.r2, last_call)
                        if res:
                            self.__to_display = f"The call {self.repr_action(last_call)} was good! "
                            self.__to_display += f"Human loses!"
                        else:
                            self.__to_display = f"The call {self.repr_action(last_call)} was a bluff! "
                            self.__to_display += f"Human wins!"
                elif self.__choose_start_screen:
                    if self.__robot_starts_button.mouse_is_above():
                        self.__choose_start_screen = False
                        self.__play_screen = True
                        self.__robot = Robot(self.__privs[0], self.__game)
                        action = self.__robot.get_action(self.__state)
                        self.__state = self.__game.apply_action(self.__state, action)
                        self.__to_display = f"Robot called {self.repr_action(action)}"
                        self.__robot_dice = self.r1
                        self.__human_dice = self.r2
                    if self.__human_starts_button.mouse_is_above():
                        self.__choose_start_screen = False
                        self.__play_screen = True
                        self.__robot = Robot(self.__privs[1], self.__game)
                        self.__robot_dice = self.r2
                        self.__human_dice = self.r1
                elif self.__end_screen:
                    if self.__continue_button.mouse_is_above():
                        self.__choose_start_screen = True
                        self.__end_screen = False
                        self.__to_display = ""
                        self.r1 = random.choice(list(self.__game.rolls(0)))
                        self.r2 = random.choice(list(self.__game.rolls(1)))
                        self.__privs = [self.__game.make_priv(self.r1, 0), self.__game.make_priv(self.r2, 1)]
                        self.__state = self.__game.make_state()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.__text_input.remove_letter()
                else:
                    self.__text_input.add_letter(event.unicode)
    def __load_images(self):
        partial_path = "source/resources/"
        for i in range(1,7):
            path = partial_path + str(i) + ".png"
            self.__images.append(pygame.image.load(path))
        robot_path = partial_path + "robot.png"
        self.__robot_image = pygame.image.load(robot_path)
        self.__robot_image = pygame.transform.scale(self.__robot_image, (100, 100))
    def __draw_human(self, dice):
        y_position = self.screen_height / 4 * 2.5
        n = len(dice)
        full_dice_length = n * 50 + (n-1) * self.__dice_image_distance
        x_position = (self.screen_width - full_dice_length)/2
        for d in dice:
            image = self.__images[d - 1]
            imagerect = (image.get_rect()).move(x_position, y_position)
            self.__screen.blit(image, imagerect)
            x_position += 50 + self.__dice_image_distance
    def __draw_robot(self, dice, visible_dice):
        imagerect = self.__robot_image.get_rect().move(self.screen_width / 2 - self.__robot_image.get_width() / 2, self.screen_height / 14)
        self.__screen.blit(self.__robot_image, imagerect)
        y_position = self.screen_height / 4
        n = len(dice)
        full_dice_length = n * 50 + (n - 1) * self.__dice_image_distance
        x_position = (self.screen_width - full_dice_length) / 2
        for d in dice:
            image = self.__images[d - 1]
            imagerect = (image.get_rect()).move(x_position, y_position)
            if visible_dice:
                self.__screen.blit(image, imagerect)
            else:
                pygame.draw.rect(self.__surface, "Black", imagerect)
            x_position += 50 + self.__dice_image_distance
    def display_on_the_middle(self):
        rect = pygame.Rect(self.screen_width / 2, self.screen_height / 2, 1, 1)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.__to_display, True, "Black")
        text_rect = text_surface.get_rect(center = rect.center)
        self.__screen.blit(text_surface, text_rect)

    def repr_action(self, action):
        action = int(action)
        if action == -1:
            return "nothing"
        if action == self.__game.LIE_ACTION:
            return "lie"
        n, d = divmod(action, self.__game.SIDES)
        n, d = n + 1, d + 1
        return f"{n} {d}s"

class Robot:
           def __init__(self, priv,game):
               self.priv = priv
               self.game = game
           def get_action(self, state):
               last_call = self.game.get_last_call(state)
               return self.game.sample_action(self.priv, state, last_call, eps=0)