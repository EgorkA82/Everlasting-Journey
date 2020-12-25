import pygame

from objects import *
from functions import *


config = Game().config

pygame.init()
pygame.display.set_caption(config['GAME_CAPTION'])

screen = pygame.display.set_mode((config['size_x'], config['size_y']))
if config['fullscreen']:
    pygame.display.toggle_fullscreen()

event_reaction = EventReaction()
active_window = ActiveWindow()
running = True

while event_reaction.running:
    event_reaction.react(pygame.event.get())
    
    active_window.show(screen)
    
    pygame.display.flip()
pygame.quit()
