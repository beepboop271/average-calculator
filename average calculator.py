import pygame
from classes.file_reader import unpack_file
from drawing.screen_elements import Window

pygame.init()

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

clock = pygame.time.Clock()
width = 1000
height = 600
display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("asdfghjkl")

courses = unpack_file("example_text_data.txt")

current_window = Window("main", width, height, (0, 0, 0))


def drawWindow(window):
    window.draw()
    display.blit(window.surface, (0, 0))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drawWindow(current_window)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
