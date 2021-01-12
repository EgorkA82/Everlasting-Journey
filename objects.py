import datetime
import json
import math
from xmlrpc.client import DateTime
import pygame

from functions import *


def load_image(path):
    return pygame.image.load(path)

def get_display_ratio():
    cfg = Config()
    return math.ceil(cfg('size_y') / cfg('size_x'))

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

def timescale(value, default_framerate=60):
    return value * (default_framerate / Game.framerate)

def timescale_int(value, default_framerate=60):
    return int(timescale(value, default_framerate))

def sizescale(value, default_scale = 80):
    return value * (default_scale / Game.scale)

class Config:
    def __init__(self):
        self.text = '''{
    "GAME_CAPTION": "[Alpha] Everlasting Journey",

    "size_x": 1280,
    "size_y": 720,
    "fullscreen": false,

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
        self.config['scale'] = int(self('size_x') / 80) # 80
        self.tile_size = self('size_x') // self('scale')

    def __call__(self, parameter):
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
    pygame.mixer.init()
    music = pygame.mixer.Sound("sounds\\background_music.wav")
    music.play(-1)
    music.set_volume(0.05)
    
    config = Config()
    framerate = config.get()["framerate"]
    scale = config.get()["scale"]
    
    def __init__(self):
        self.world = World(self)
        self.player = Player("Player", self)
        self.camera = Camera(self)
    
    def get_center(self):
        return [self.config.get()['size_x'] // 2, self.config.get()['size_y'] // 2]

    def display(self, screen):
        self.camera.draw(screen)
        screen.blit(self.night_layer, (0, 0))


class World:
    def __init__(self, game):
        self.game = game
        self.time = datetime.datetime.now().replace(hour=12, minute = 0, second=0, microsecond=0)
        self.tile_size = Config().get_tile_size()
        self.create_board()

    def create_board(self):
        board = []
        for row in range(0, (self.game.config.get()['size_y'] // Tiles.absolute_size + 1)): # y
            board.append([])
            for tile in range(0, (self.game.config.get()['size_x'] // Tiles.absolute_size + 1)): # x
                board[row] += [Grass([tile, row])]
        self.board = board
    
    def width(self):
        return (len(self.board[0])) * self.game.config.get_tile_size()
    
    def height(self):
        return (len(self.board)) * self.game.config.get_tile_size()
    
    def get_center(self): # от начала карты
        return ((self.game.config.get()['size_x'] - self.width()) / 2, (self.game.config.get()['size_y'] - self.height()) / 2)


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


class EventReaction:
    def __init__(self, game, night_layer):
        self.running = True
        self.iteration = 0
        self.increase_time_speed = (1 // timescale(0.1))
        self.night_layer_change_speed = self.increase_time_speed * 5
        self.game = game
        self.game.night_layer = night_layer
        self.night_layer = night_layer
        self.night_layer_change()

    def react(self, events):
        self.iteration += 1
        self.iteration %= timescale_int(1000000000)
        
        if self.iteration % self.increase_time_speed == 0:
            self.increase_time()
            if self.iteration % self.night_layer_change_speed == 0:
                self.night_layer_change()
        
        for event in events:
            if self.check_quit(event): return
            self.player_move(event)
    
        if any([self.game.player.direction_x, self.game.player.direction_y]) != 0:
            self.game.player.move((self.game.player.direction_x, self.game.player.direction_y), self.iteration)
            # self.game.camera.set_center(self.game.player.rect.center)

    def player_move(self, event):
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
            if event.key == pygame.K_w:
                self.game.player.direction_y += 1
            elif event.key == pygame.K_a:
                self.game.player.direction_x += -1
            elif event.key == pygame.K_s:
                self.game.player.direction_y += -1
            elif event.key == pygame.K_d:
                self.game.player.direction_x += 1
        elif event.type == pygame.KEYUP and event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
            if event.key == pygame.K_w:
                self.game.player.direction_y += -1
                self.game.player.set_direction(up=True)
            elif event.key == pygame.K_a:
                self.game.player.direction_x += 1
                self.game.player.set_direction(left=True)
            elif event.key == pygame.K_s:
                self.game.player.direction_y += 1
                self.game.player.set_direction(down=True)
            elif event.key == pygame.K_d:
                self.game.player.direction_x += -1
                self.game.player.set_direction(right=True)
                 
    def check_quit(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return True
        return False
    
    def increase_time(self):
        self.game.world.time += datetime.timedelta(minutes=1)

    def night_layer_change(self):
        highest_tranparency = 40
        
        transparency = highest_tranparency  * 2.55 * (math.cos(
            (self.game.world.time - datetime.datetime.combine(
                self.game.world.time, datetime.time(3, 00)
                )
             ).total_seconds() / 60 / 60 * math.pi / 12) + 1) / 2
            
        self.night_layer.fill(pygame.Color(0, 0, 255))
        self.night_layer.set_alpha(transparency)    

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

    
class NPC:
    cfg = Config()
    mixer_initialized = False
    try:
        pygame.mixer.init()
        mixer_initialized = True
    except:
        pass
    
    def __init__(self, name, pos, game, health, image_src, weight=55):
        self.size_per_tile = 0.9
        self.frames = scale_image(AnimatedSprite.cut_sheet(
            load_image(image_src), 3, 4), 
            size=(
                int(self.cfg.get_tile_size() * self.size_per_tile),
                int(self.cfg.get_tile_size() * self.size_per_tile)
            ))
        self.image = self.frames[1]
        self.rect = self.image.get_rect()
        self.name = name
        self.max_health = health
        self.pos = pos
        self.health = health
        self.weight = weight
        self.game = game
        self.default_velocity = sizescale(0.2)
        self.velocity = self.get_velocity()
        self.animation_speed = timescale_int(24) # lower - faster
        self.previous_animation_num = None
        
        if self.mixer_initialized:
            self.walking_sound = pygame.mixer.Sound('sounds\\walking.wav')
            self.walking_sound.set_volume(0.1)

    def set_pos(self, pos):
        self.pos = pos

    def set_direction(self, up=False, right=False, down=False, left=False, move=False):
        if up + right + down + left != 1:
            raise Exception("Direction is not stated correctly")
        else:
            if not move:
                if up:
                    self.image = self.frames[10]
                elif right:
                    self.image = self.frames[7]
                elif down:
                    self.image = self.frames[1]
                elif left:
                    self.image = self.frames[4]
    
    def move(self, offset, iteration):
        animation_num = int(iteration // timescale(self.animation_speed) % 3)
        if offset[0] != 0:
            if offset[0] > 0:
                self.image = self.frames[6 + animation_num]
            if offset[0] < 0:
                self.image = self.frames[3 + animation_num]
        elif offset[1] != 0:
            if offset[1] > 0:
                self.image = self.frames[9 + animation_num]
            if offset[1] < 0:
                self.image = self.frames[animation_num]
                
        if abs(offset[0]) == abs(offset[1]) != 0:
            if 0 + self.rect.w / 2 <= self.rect.centerx + sizescale(offset[0]) * 0.75 * self.get_velocity() <= self.cfg.get()['size_x'] - self.rect.w / 2:
                self.rect.centerx += sizescale(offset[0]) * 0.75 * self.get_velocity()
            if 0 + self.rect.h / 2 <= self.rect.centery - sizescale(offset[1]) * 0.75 * self.get_velocity() <= self.cfg.get()['size_y'] - self.rect.h / 2:
                self.rect.centery -= sizescale(offset[1]) * 0.75 * self.get_velocity()
        else:
            if 0 + self.rect.w / 2 <= self.rect.centerx + sizescale(offset[0]) * self.get_velocity() <= self.cfg.get()['size_x'] - self.rect.w / 2:
                self.rect.centerx += sizescale(offset[0]) * self.get_velocity()
            if 0 + self.rect.h / 2 <= self.rect.centery - sizescale(offset[1]) * self.get_velocity() <= self.cfg.get()['size_y'] - self.rect.h / 2:
                self.rect.centery -= sizescale(offset[1]) * self.get_velocity()
        self.pos = [self.rect.x, self.rect.y]
        
        if offset[0] == offset[1] == 0:
            if self.mixer_initialized:
                self.walking_sound.stop()
        
        if self.previous_animation_num != animation_num:
            try:
                self.walking_sound.stop()
            except:
                pass
            if self.mixer_initialized:
                self.walking_sound.play(maxtime=220)
            self.previous_animation_num = animation_num
    
    def get_total_weight(self):
        return self.weight + self.inventory.get_weight()

    def get_velocity(self):
        return self.default_velocity

    def set_health(self, health):
        self.health = health

    def change_health(self, health_change):
        if (self.health + health_change <= self.max_health) and (self.health + health_change >= 0):
            self.health = self.health + health_change
        elif self.health + health_change < 0:
            self.health = 0
        elif self.health + health_change > self.max_health:
            self.health = self.max_health


class Player(pygame.sprite.Sprite, NPC):
    player_sprite = pygame.sprite.Group()
    
    def __init__(self, player_name, game, inventory=Inventory(), health=100, weight=50):
        super().__init__(self.player_sprite)
        NPC.__init__(self, player_name, [0, 0], game, health, "sprites\\objects\\npc\\female.png", weight)
        self.pos = [self.rect.center[0] - self.rect.w, self.rect.center[1] - self.rect.h]
        self.rect.center = self.game.get_center()
        self.inventory = inventory
        self.is_moving = False
        self.direction_x = 0
        self.direction_y = 0

    def center(self, camera_pos): # отступ от края с учетом позиции камеры
        self.rect.centerx = camera_pos[0] + self.game.world.width() / 2
        self.rect.centery = camera_pos[1] + self.game.world.height() / 2
        self.pos = [self.rect.x, self.rect.y]

    def __str__(self):
        return f"player_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()


class Objects:
    all_objects = pygame.sprite.Group()


class Tiles(pygame.sprite.Sprite):
    cfg = Config()
    absolute_size = cfg.get_tile_size()
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
        self.rect.centerx = self.pos[0] + camera_pos[0]
        self.rect.centery = self.pos[1] + camera_pos[1]

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
    image = scale_image(load_image("sprites/objects/tiles/grass.jpg"), size=(cfg.get_tile_size(), cfg.get_tile_size()))
    
    def __init__(self, board_pos, is_stackable=False, is_placed=True):
        super().__init__(__class__.__name__, board_pos, is_stackable, is_placed)
        
    def __str__(self):
        return super().__str__()
    
    def __repr__(self):
        return super().__repr__()


class UI(pygame.sprite.Sprite):
    all_ui = pygame.sprite.Group()
    
    def __init__(self, game):
        super().__init__(self.all_ui)
        self.game = game
    
    def display_inventory(self):
        pass
    
    def get_inventory_center(self, item_num):
        pass
    
    def display_clock(self):
        pass
    
    def update(self):
        pass
        

class Camera:
    cfg = Config()
    
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(Tiles.all_tiles,  Objects.all_objects, self.player.player_sprite)
        self.pos = [0, 0]
        self.update(self.pos)
    
    def update(self, pos, exception=[]): # обновление позиции относительно камеры
        all_sprites = self.all_sprites.copy()
        all_sprites.remove(exception)
        all_sprites.update(pos)
         
    def set(self, pos):
        self.pos = pos
        self.update(self.pos)

    def set_center(self, pos):
        if self.is_movable([pos[0], 0]):
            self.pos[0] = self.game.get_center()[0] - pos[0]
        if self.is_movable([0, pos[1]]):
            self.pos[1] = self.game.get_center()[1] - pos[1]
        self.update(self.pos)
    
    def is_movable(self, offset):
        print(self.pos[0] - offset[0], self.game.world.game.get_center()[0])
        return abs(self.pos[0] - offset[0]) <= abs(self.game.world.game.get_center()[0]) and abs(self.pos[1] - offset[1]) <= abs(self.game.world.game.get_center()[1])
    
    def draw(self, screen):
        self.all_sprites.draw(screen)
