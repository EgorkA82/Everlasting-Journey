import datetime
import json
import random
import math
import sys
import pygame

from functions import *


def load_image(path):
    return pygame.image.load(path)

def get_tile_num():
    cfg = Config()
    return math.ceil(cfg('size_x') / cfg('scale'))

def get_display_ratio():
    cfg = Config()
    return math.ceil(cfg('size_y') / cfg('size_x'))

def load_image(path):
    return pygame.image.load(path)

def scale_image(image, size):
    return pygame.transform.scale(image, size)


class Config:
    def __init__(self):
        self.text = '''{
    "GAME_CAPTION": "[Alpha] Everlasting Journey",

    "size_x": 1280,
    "size_y": 720,
    "fullscreen": false,

    "scale": 50,
    "framerate": 60
} '''
        self.defaults = json.loads(self.text)
        try:
            with open("config.json", "r", encoding="utf-8") as config:
                self.config = json.load(config)
        except FileNotFoundError:
            with open("config.json", "w", encoding="utf-8") as config:
                config.write(self.text)
            self.set_defaults()

        self.tile_size = self('size_x') // self('scale')

    def __call__(self, parameter):
        if parameter == 'scale':
            return self.config['size_y'] // self.config[parameter]
        return self.config[parameter]

    def set_defaults(self):
        self.config = self.defaults

    def get(self):
        return self.config

    def get_tile_size(self):
        return self.tile_size


class Menu:
    def display(self, screen):
        pass


class Game:
    def __init__(self, config=Config().get()):
        self.config = config
        self.world = World()
        self.camera = Camera(self)

    def config(self, pamameter):
        return self.config[pamameter]

    def display(self, screen):
        # self.camera.move((-10, -10))
        self.camera.draw(screen)


class World:
    def __init__(self):
        self.time = datetime.datetime.now()
        self.tile_size = Config().get_tile_size()
        self.board = self.create_board()

    def create_board(self):
        board = []
        for row in range(0, get_tile_num() * get_display_ratio()): # y
            board.append([])
            for tile in range(0, get_tile_num()): # x
                board[row] += [Grass((tile, row))]
        return board


class ActiveWindow:
    def __init__(self, window):
        self.current_window = window

    def show(self, screen):
        self.current_window.display(screen)

    def set(self, window):
        self.current_window = window


class Inventory:
    def __init__(self, size=[[0] * 6] * 4):
        self.size = size

    def get_weight(self):
        return 0  #######################################


class NPC:
    def __init__(self, name, pos, health, heigth=5, is_friendly=True, weight=55):
        self.name = name
        self.max_health = health
        self.health = health
        self.pos = pos
        self.heigth = heigth
        self.is_friendly = is_friendly
        self.weight = weight

    def set_health(self, health):
        self.health = health

    def change_health(self, health_change):
        if (self.health + health_change <= self.max_health) and (self.health + health_change >= 0):
            self.health = self.health + health_change
        elif self.health + health_change < 0:
            self.health = 0
        elif self.health + health_change > self.max_health:
            self.health = self.max_health


class Player:
    def __init__(self, player_name, pos, inventory=Inventory(), health=100, height=5, weight=50):
        self.name = player_name
        self.pos = pos
        self.health = health
        self.height = height
        self.weight = weight
        self.inventory = inventory
        self.default_velocity = 100
        self.velocity = self.get_velocity()

    def set_pos(self, pos):
        self.pos = pos

    def get_total_weight(self):
        return self.weight + self.inventory.get_weight()

    def get_velocity(self):
        return int(self.default_velocity * (1 / self.get_total_weight()))


class Objects:
    all_objects = pygame.sprite.Group()


class Tiles(pygame.sprite.Sprite):
    absolute_size = Config().get_tile_size()
    all_tiles = pygame.sprite.Group()

    def __init__(self, name, board_pos, is_stackable=False, is_placed=True):
        super().__init__(Tiles.all_tiles)
        self.name = name
        self.weight = 1
        self.is_stackable = is_stackable
        self.is_placed = is_placed
        self.rect = self.image.get_rect()
        self.board_pos = board_pos
        self.pos = [board_pos[0] * self.absolute_size, board_pos[1] * self.absolute_size]
        
    def update(self, camera_pos):
        self.rect.x = camera_pos[0] + self.board_pos[0] * self.absolute_size
        self.rect.y = camera_pos[1] + self.board_pos[0] * self.absolute_size
        self.pos = [self.rect.x, self.rect.y]
        print(self, self.rect)

    def set_name(self, name):
        self.name = name

    def get_pos(self):
        return self.pos

    def __str__(self):
        return f"tile_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()


class Quest:
    def __init__(self, text, requester, condition, completed_text):
        self.text = text
        self.requester = requester
        self.condition = condition
        self.completed_text = completed_text
        self.completed = False

    def check_for_completed(self):
        if eval(self.condition):
            self.set_completed()

    def set_completed(self):
        self.completed = True


class EventReaction:
    def __init__(self):
        self.running = True
        self.iteration = 0

    def react(self, events, game):
        self.iteration += 1
        
        for event in events:
            if self.check_quit(event): return
        
        if self.iteration % 200 == 0:
            self.increase_time(game)

    def check_quit(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return True
        return False
    
    def increase_time(self, game):
        game.world.time += datetime.timedelta(minutes=1)


class Grass(Tiles):
    cfg = Config()
    image = scale_image(load_image("sprites/objects/tiles/grass.jpg"), (cfg.get_tile_size(), cfg.get_tile_size()))
    
    def __init__(self, board_pos, is_stackable=False, is_placed=True):
        super().__init__(self, board_pos, is_stackable, is_placed)
        Tiles.__init__(self, name=__class__.__name__, board_pos=board_pos, is_stackable=is_stackable, is_placed=is_placed)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos
        
    def __str__(self):
        return super().__str__()
    
    def __repr__(self):
        return super().__repr__()


class UI:
    pass
    

class Camera:
    cfg = Config()
    
    def __init__(self, game):
        self.game = game
        self.all_sprites = pygame.sprite.Group()
        objects = Objects
        tiles = Tiles
        self.all_sprites.add(objects.all_objects, tiles.all_tiles)
        self.center()
    
    def center(self):
        self.pos = [(self.cfg('size_x') - (len(self.game.world.board[0]) / 2) * self.cfg.get_tile_size()) / 2,
                    (self.cfg('size_y') - (len(self.game.world.board) / 2) * self.cfg.get_tile_size()) / 2
                    ] # camera's centering
        
        print(f"Camera's pos: {self.pos}")
        print(f"Board's width: {(len(self.game.world.board[0]) / 2) * self.cfg.get_tile_size() / 2}")
        print(f"Board's height: {(len(self.game.world.board) / 2) * self.cfg.get_tile_size() / 2}")
        self.update(self.pos)
    
    def update(self, pos):
        self.all_sprites.update(pos)
            
    def set(self, pos):
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.update(pos)

    def move(self, offset):
        self.update((self.pos[0] + offset[0], self.pos[1] + offset[1]))
        
    def draw(self, screen):
        self.all_sprites.draw(screen)