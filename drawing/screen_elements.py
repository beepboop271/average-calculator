import pygame


class Window(object):
    def __init__(self, name, width, height, colour):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((self.width, self.height))
        self.name = name
        self.elements = []
        self.background_colour = colour

    def draw(self):
        self.surface.fill(self.background_colour)
        for element in self.elements:
            element.draw(self.surface)


class Button(object):
    def __init__(self, name):
        self.name = name
