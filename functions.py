import pygame

import objects


def load_image(path):
    return pygame.image.load(path)

def y_from_bottom(y):
    return objects.Game('size_y') - y