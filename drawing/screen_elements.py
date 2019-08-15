import pygame


class Window(object):
    def __init__(self, name, width, height, colour, display):
        self.name = name
        self.width = max(width, display.get_width())
        self.height = max(height, display.get_height())
        self.background_colour = colour
        self.display = display

        self.visible_top = 0
        self.surface = pygame.Surface((self.width, self.height))
        self.elements = []

    def draw(self):
        self.surface.fill(self.background_colour)
        for element in self.elements:
            element.draw(self.surface)

    def scroll(self, dy):
        self.visible_top = min(max(self.visible_top+dy, 0), self.height-self.display.get_height())


class Button(object):
    def __init__(self, name, center_x, center_y, width, height, colour, text):
        self.name = name
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (center_x, center_y)
        self.width = width
        self.height = height
        self.colour = colour
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, self.colour, self.rect)
