import pygame


class TextInput:
    __text = ""
    __text_color = "White"
    __color = "Blue"
    __font_size = 32
    def __init__(self, middle_x, middle_y, width, height):
        self.__middle_x = middle_x
        self.__middle_y = middle_y
        self.__rect = pygame.Rect(middle_x - width/2, middle_y - height/2, width, height)
        self.__font = pygame.font.Font(None, self.__font_size)
    def add_letter(self, char):
        if(len(self.__text) <= 2):
            self.__text += char
    def remove_letter(self):
        self.__text = self.__text[:-1]
    def clear(self):
        self.__text = ""
    def get_text(self):
        return self.__text
    def draw(self, surface, screen):
        pygame.draw.rect(surface, self.__color, self.__rect, 5)
        text_surface = self.__font.render(self.__text, True, self.__text_color)
        text_rect = text_surface.get_rect(center=self.__rect.center)
        screen.blit(text_surface, text_rect)
