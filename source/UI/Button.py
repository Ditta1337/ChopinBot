import pygame
class Button:
    __neutral_color = "Blue"
    __mouse_over_button = "Dark Blue"
    __current_color = "Blue"
    __text_color = "White"
    def __init__(self, middle_x: int, middle_y: int, width: int, height: int, text: str):
        self.__button_rect = pygame.Rect(middle_x - width / 2, middle_y - height / 2,
                                width, height)
        text = text
        font = pygame.font.Font(None, 36)
        self.__text_surface = font.render(text, True, self.__text_color)
        self.__text_rect = self.__text_surface.get_rect(center = self.__button_rect.center)
    def update(self, mouse_pos):
        if self.__button_rect.collidepoint(mouse_pos):
            self.__current_color = self.__mouse_over_button
        else:
            self.__current_color = self.__neutral_color
    def mouse_is_above(self):
        return self.__current_color == self.__mouse_over_button
    def draw(self, surface, screen):
        pygame.draw.rect(surface, self.__current_color, self.__button_rect)
        screen.blit(self.__text_surface, self.__text_rect)