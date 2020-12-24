import datetime
import json
import random
import math
import pygame

from functions import *


def load_image(path):
    return pygame.image.load(path)

def y_from_bottom(y):
    return Game('size_y') - y

def get_tile_num():
    return math.ceil(Config('size_x') / Config('scale'))

def load_image(path):
    return pygame.image.load(path)


class Config:
    def __init__(self):

        self.text = '''{
                           "GAME_CAPTION": "Everlasting Journey",

                           "size_x": 1280,
                           "size_y": 720,
                           "fullscreen": false,

                           "scale": 50
                       }'''
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
        return self.config[parameter]

    def set_defaults(self):
        self.config = self.defaults

    def get(self):
        return self.config

    def get_tile_size(self):
        return self.tile_size


class Game:
    def __init__(self, config=Config().get()):
        self.config = config
        self.world = World()

    def config(self, pamameter):
        return self.config[pamameter]

    def display(self):
        for tile in self.world.board:
            Tile.all_tiles.draw()


class Menu:
    def display(self):
        pass


class World:
    def __init__(self):
        self.time = datetime.datetime.now()
        self.tile_size = Config().get_tile_size()
        self.is_rainy = False
        self.board = self.create_board()

    def create_board(self):
        board = []
        for row in range(0, get_tile_num()):
            board.append([])
            for tile in range(0, get_tile_num() * Config('size_y') // Config('size_x')):
                board[row] += [Tile('grass', (tile * Tile.absolute_size, row * Tile.absolute_size))]
        self.board = board

    def set_weather_rainy(self, rainy=True):
        self.is_rainy = rainy


class ActiveWindow:
    def __init__(self):
        self.current_window = Game()

    def show(self):
        self.current_window.display()

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

    def set_pos(self, x, y):
        self.pos = (x, y_from_bottom(y))

    def get_total_weight(self):
        return self.weight + self.inventory.get_weight()

    def get_velocity(self):
        return int(self.default_velocity * (1 / self.get_total_weight()))


class Tile:
    absolute_size = Config().get_tile_size()
    all_tiles = pygame.sprite.Group()

    def __init__(self, name, pos, is_stackable=False, is_placed=True):
        self.name = name
        self.pos = pos
        self.weight = 1
        self.is_stackable = is_stackable
        self.is_placed = is_placed
        self.all_tiles.add(self)

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

    def react(self, events):
        for event in events:
            self.check_quit(event)

    def check_quit(self, event):
        if event.type == pygame.QUIT:
            self.running = False


class Grass(pygame.sprite.Sprite):
    image = load_image("sprites/objects/tiles/grass.jpg")
    all_sprites = pygame.sprite.Group()
    
    def __init__(self, name, pos, is_stackable, is_placed, group=all_sprites):
        super().__init__(*group)
        self.image = Grass.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        Tile.__init__(__class__.__name__, pos, is_stackable=is_stackable, is_placed=is_placed)


