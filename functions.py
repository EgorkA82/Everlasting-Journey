import pygame


def load_image(path):
    return pygame.image.load(path)

def load_image(path, **kwargs):
    return pygame.image.load(path, *kwargs)

def scale_image(*images, size):
    size = [int(size[0]), int(size[1])]
    if images[0].__class__.__name__ != [].__class__.__name__: # если масштабируем один
        return pygame.transform.scale(images[0], size)
    else: # если масштабируем несколько
        frames = []
        for image in images[0]:
            frames.append(pygame.transform.scale(image, size))
        return frames
