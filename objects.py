from json import load
import pygame
from functions import Tile, load_image


class Grass(pygame.sprite.Sprite):
    image = load_image("sprites/objects/tiles/grass.jpg")
    all_sprites = pygame.sprite.Group()
    
    def __init__(self, name, pos, is_stackable, is_placed, group=all_sprites):
        super().__init__(*group)
        self.image = Grass.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        Tile.__init__(__class__.__name__, pos, is_stackable=is_stackable, is_placed=is_placed)


