import pygame
from classes.file_reader import unpack_file
from drawing.screen_elements import Window, Button

pygame.init()

STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

BACKGROUND_CLR = (18, 18, 18)
ELEMENT_CLR = (49, 49, 49)
TEXT_CLR = (144, 144, 144)

clock = pygame.time.Clock()
MOUSE_SCROLL_UP = 4
MOUSE_SCROLL_DOWN = 5
MOUSE_SCROLL_AMOUNT = 12
width = 1000
height = 600
display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("asdfghjkl")

courses = unpack_file("example_text_data.txt")
current_window = Window("main", width, 200+(len(courses)*150), BACKGROUND_CLR, display)
for i in range(len(courses)):
    current_window.elements.append(Button(courses[i].course, width/2, 200+(150*i + 75), 700, 100, ELEMENT_CLR, courses[i].course))


def drawWindow(window):
    window.draw()
    display.blit(window.surface, (0, -window.visible_top))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == MOUSE_SCROLL_UP:
                current_window.scroll(-MOUSE_SCROLL_AMOUNT)
            elif event.button == MOUSE_SCROLL_DOWN:
                current_window.scroll(MOUSE_SCROLL_AMOUNT)

    drawWindow(current_window)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
