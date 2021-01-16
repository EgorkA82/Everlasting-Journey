import pygame


def load_image(path):
    return pygame.image.load(path)

def load_image(path, **kwargs):
    return pygame.image.load(path, *kwargs)

def scale_image(*images, size):
    if images[0].__class__.__name__ != [].__class__.__name__:
        return pygame.transform.scale(images[0], size)
    else:
        frames = []
        for image in images[0]:
            frames.append(pygame.transform.scale(image, size))
        return frames
