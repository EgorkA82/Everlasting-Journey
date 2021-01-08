import pygame

from objects import *
from functions import *

clock = pygame.time.Clock()
game = Game()
config = game.config

pygame.init()
pygame.display.set_caption(config.get()['GAME_CAPTION'])

screen = pygame.display.set_mode((config.get()['size_x'], config.get()['size_y']))
night_layer = pygame.Surface((config.get()['size_x'], config.get()['size_y']), pygame.SRCALPHA)
if config.get()['fullscreen']:
    pygame.display.toggle_fullscreen()

event_reaction = EventReaction(game, night_layer=night_layer)
active_window = ActiveWindow(game)
running = True

while event_reaction.running:
    event_reaction.react(pygame.event.get())

    screen.fill(pygame.Color('#f2f2f2'))
    active_window.show(screen)
    pygame.display.flip()
    
    clock.tick(game.framerate)
pygame.quit()
