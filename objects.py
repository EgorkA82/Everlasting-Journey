import datetime
import json
import random
import math
import sys
from time import time
from turtle import width
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

def load_image(path, **kwargs):
    return pygame.image.load(path, *kwargs)

def scale_image(image, size):
    return pygame.transform.scale(image, size)

def timescale(value, default_framerate=60):
    return value * (default_framerate / Game.framerate)

def timescale_int(value, default_framerate=60):
    return int(timescale(value, default_framerate))


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
    framerate = Config().get()["framerate"]
    
    def __init__(self, config=Config()):
        self.config = config
        self.world = World(self)
        self.player = Player("Player", self)
        self.camera = Camera(self)
        

    def config(self, pamameter):
        return self.config[pamameter]
    
    def center(self):
        return (self.config.get()['size_x'] // 2, self.config.get()['size_y'] // 2)

    def display(self, screen):
        self.player.move((-10, 0))
        self.camera.draw(screen)


class World:
    def __init__(self, game):
        self.game = game
        self.time = datetime.datetime.now()
        self.tile_size = Config().get_tile_size()
        self.board = self.create_board()

    def create_board(self):
        board = []
        for row in range(0, get_tile_num() * get_display_ratio()): # y
            board.append([])
            for tile in range(0, get_tile_num()): # x
                board[row] += [Grass([tile, row])]
        return board
    
    def width(self):
        return (len(self.board[0])) * self.game.config.get_tile_size()
    
    def height(self):
        return (len(self.board)) * self.game.config.get_tile_size()
    
    def center(self): # от начала карты
        return ((super().config.get()['size_x'] - self.width()) / 2, (super().config.get()['size_y'] - self.height()) / 2)


class ActiveWindow:
    def __init__(self, window):
        self.current_window = window

    def show(self, screen):
        self.current_window.display(screen)

    def set(self, window):
        self.current_window = window


class Inventory:
    def __init__(self, size=[[0] * 10]):
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


class EventReaction:
    def __init__(self, game):
        self.running = True
        self.iteration = 0
        self.game = game

    def react(self, events):
        self.iteration += 1
        
        if self.iteration % timescale_int(200) == 0:
            self.increase_time()
        
        for event in events:
            if self.check_quit(event): return
            elif self.player_move(event): return

    def player_move(self, event):
        if event.type == pygame.KEYDOWN:
            pass
                
    def check_quit(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return True
        return False
    
    def increase_time(self):
        self.game.world.time += datetime.timedelta(minutes=1)


class AnimatedSprite:
    def cut_sheet(sheet, columns, rows):
        frames = []
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, 
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, rect.size)))
        return frames


class Player(pygame.sprite.Sprite):
    cfg = Config()
    
    player_sprite = pygame.sprite.Group()
    
    def __init__(self, player_name, game, inventory=Inventory(), health=100, weight=50):
        self.size_per_tile = 0.9
        super().__init__(self.player_sprite)
        self.frames = AnimatedSprite.cut_sheet(
            (scale_image(load_image("sprites\\objects\\npc\\male.png"), (
                int(self.cfg.get_tile_size() * 3 * self.size_per_tile),
                int(self.cfg.get_tile_size() * 4 * self.size_per_tile)
                ))),
            3, 4)
        self.image = self.frames[1]
        self.rect = self.image.get_rect()
        self.rect.center = game.center()
        self.pos = [self.rect.center[0] - self.rect.w, self.rect.center[1] - self.rect.h]
        self.name = player_name
        self.game= game
        self.health = health
        self.weight = weight
        self.inventory = inventory
        self.default_velocity = 100
        self.velocity = self.get_velocity()

    def center(self, camera_pos): # отступ от края с учетом позиции камеры
        self.rect.centerx = camera_pos[0] + self.game.world.width() / 2
        self.rect.centery = camera_pos[1] + self.game.world.height() / 2
        self.pos = [self.rect.x, self.rect.y]
    
    def set_pos(self, pos):
        self.pos = pos

    def move(self, offset):
        self.pos[0] += offset[0]
        self.pos[1] += offset[1]
    
    def get_total_weight(self):
        return self.weight + self.inventory.get_weight()

    def get_velocity(self):
        return max(self.default_velocity * 0.2, 
                   int(self.default_velocity - (0.5 * self.get_total_weight())))

    def __str__(self):
        return f"player_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()


class Objects:
    all_objects = pygame.sprite.Group()


class Tiles(pygame.sprite.Sprite):
    absolute_size = Config().get_tile_size()
    all_tiles = pygame.sprite.Group()

    def __init__(self, name, board_pos, is_stackable=False, is_placed=True):
        super().__init__(self.all_tiles)
        self.name = name
        self.weight = 1
        self.is_stackable = is_stackable
        self.is_placed = is_placed
        self.rect = self.image.get_rect()
        self.board_pos = board_pos
        self.pos = [board_pos[0] * self.absolute_size, board_pos[1] * self.absolute_size]
        
    def update(self, camera_pos): # отступ от края с учетом позиции камеры
        self.rect.x = camera_pos[0] + self.pos[0]
        self.rect.y = camera_pos[1] + self.pos[1]
        self.pos = [self.rect.x, self.rect.y]

    def set_name(self, name):
        self.name = name

    def get_pos(self):
        return self.pos

    def __str__(self):
        return f"tile_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()


class Grass(Tiles):
    cfg = Config()
    image = scale_image(load_image("sprites/objects/tiles/grass.jpg"), (cfg.get_tile_size(), cfg.get_tile_size()))
    
    def __init__(self, board_pos, is_stackable=False, is_placed=True):
        super().__init__(__class__.__name__, board_pos, is_stackable, is_placed)
        
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
        self.player = game.player
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(Tiles.all_tiles,  Objects.all_objects, self.player.player_sprite)
        self.center()
    
    def center(self):
        self.pos = [(self.cfg('size_x') - (len(self.game.world.board[0])) * self.cfg.get_tile_size()) / 2,
                    (self.cfg('size_y') - (len(self.game.world.board)) * self.cfg.get_tile_size()) / 2
                    ] # camera's centering
        
        print(f"Camera's pos: {self.pos}")
        print(f"Board's width: {(len(self.game.world.board[0])) * self.cfg.get_tile_size()}")
        print(f"Board's height: {(len(self.game.world.board)) * self.cfg.get_tile_size()}")
        self.update(self.pos)
    
    def update(self, pos):
        self.all_sprites.update(pos)
            
    def set(self, pos):
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.update(pos)

    def move(self, offset):
        self.pos[0] += offset[0]
        self.pos[1] += offset[1]
        self.update((self.pos[0] + offset[0], self.pos[1] + offset[1]))
        
    def draw(self, screen):
        self.all_sprites.draw(screen)
