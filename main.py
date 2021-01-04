import pygame

from objects import *
from functions import *

clock = pygame.time.Clock()
game = Game()
config = game.config

pygame.init()
pygame.display.set_caption(config.get()['GAME_CAPTION'])

screen = pygame.display.set_mode((config.get()['size_x'], config.get()['size_y']))
if config.get()['fullscreen']:
    pygame.display.toggle_fullscreen()

event_reaction = EventReaction()
active_window = ActiveWindow(game)
running = True

while event_reaction.running:
    event_reaction.react(pygame.event.get())

    clock.tick(config.get()['framerate'])
    screen.fill(pygame.Color('#f2f2f2'))
    active_window.show(screen)
    pygame.display.flip()
pygame.quit()
