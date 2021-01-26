import functions
import objects
import pygame
    

class Tiles(pygame.sprite.Sprite):
    cfg = objects.Config()
    absolute_size = cfg.get_tile_size()
    all_tiles = pygame.sprite.Group()
    
    def __init__(self, name, board_pos, is_stackable=False, is_placed=True):
        super().__init__(self.all_tiles)
        self.name = name
        self.is_stackable = is_stackable
        self.is_placed = is_placed
        self.rect = self.image.get_rect()
        self.board_pos = board_pos
        self.pos = [board_pos[0] * self.absolute_size, board_pos[1] * self.absolute_size]
        
    def update(self, camera_pos): # отступ от края с учетом позиции камеры
        self.rect.x = self.rect.x - camera_pos[0]
        self.rect.centery = self.rect.centery - camera_pos[1]

    def place(self, pos):
        self.rect.x = self.pos[0] - pos[0]
        self.rect.centery = self.pos[1] - pos[1]
    
    def set_name(self, name):
        self.name = name

    def get_pos(self):
        return self.pos

    def __str__(self):
        return f"tile_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()


class Grass(Tiles):
    image = functions.scale_image(functions.load_image("sprites\\objects\\tiles\\grass.jpg"), size=(Tiles.cfg.get_tile_size(), Tiles.cfg.get_tile_size()))
    
    def __init__(self, board_pos,):
        super().__init__(__class__.__name__, board_pos)
