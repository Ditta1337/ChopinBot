import pygame
from sys import exit
from .Button import Button
from .TextInput import TextInput
class UI:
    screen_width = 800
    screen_height = 600

    def initialize(self):
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("ChopinBot")
        clock = pygame.time.Clock()
        self.__check_button = Button(self.screen_width / 4 * 3, self.screen_height / 8 * 7, 100, 50, "check")
        self.__bet_button = Button(self.screen_width / 4, self.screen_height / 8 * 7, 100, 50, "bet")
        self.__text_input = TextInput(self.screen_width / 4 * 2, self.screen_height / 8 * 7, 100, 50)
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill('Dark Green')

        myimage = pygame.image.load("resources/1.png")
        imagerect = myimage.get_rect()


        while True:
            self.__event_handler()
            self.__check_button.update(pygame.mouse.get_pos())
            self.__bet_button.update(pygame.mouse.get_pos())

            screen.blit(surface, (0, 0))
            self.__check_button.draw(surface, screen)
            self.__bet_button.draw(surface, screen)
            self.__text_input.draw(surface, screen)

            #screen.blit(myimage, imagerect)

            pygame.display.update()
            clock.tick(30)

    def __event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if(self.__bet_button.mouse_is_above()):
                    print(self.__text_input.get_text())
                    self.__text_input.clear()
                elif(self.__check_button.mouse_is_above()):
                    print("Check!")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.__text_input.remove_letter()
                else:
                    self.__text_input.add_letter(event.unicode)