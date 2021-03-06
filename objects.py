import datetime
import json
import math
import pygame
import random

from functions import *


class Config:
    def __init__(self):
        self.text = '''{
    "GAME_CAPTION": "[Beta] Everlasting Journey",

    "size_x": 1280,
    "size_y": 720,
    "fullscreen": false,

    "framerate": 60}'''
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

    def get_display_ratio(self):
        return math.ceil(self('size_y') / self('size_x'))


class Menu:
    def display(self, screen):
        config = Game.config
        background = scale_image(load_image("sprites\\menu_background.png"), size=[config.get()["size_x"], config.get()["size_y"]])
        background
        screen.blit(background, [0, 0])


class Game:
    import tiles
    import npc
    
    config = Config()
    framerate = config.get()["framerate"]
    scale = config.get()["scale"]
    
    def __init__(self):
        self.world = World(self)
        self.player = self.npc.Player("Player", self)
        self.world.create_coins(10)
        self.camera = Camera(self)
        self.ui = UI(self)
        
        try:
            pygame.mixer.init()
            self.music = pygame.mixer.Sound('sounds\music.wav')
            self.music.play(-1)
            self.music.set_volume(0.1)
        except:
            pass
    
    def get_center(self):
        return [self.width() // 2, self.height() // 2]

    def width(self):
        return self.config.get()['size_x']

    def height(self):
        return self.config.get()['size_y']

    def display(self, screen):
        self.screen = screen
        
        self.screen.fill(pygame.Color('#f2f2f2'))
        self.camera.draw(self.screen)
        self.screen.blit(self.night_layer, (0, 0))
        self.ui.display_quest(screen)

    def timescale(self, value, default_framerate=60):
        return value * (default_framerate / self.framerate)

    def timescale_int(self, value, default_framerate=60):
        return int(self.timescale(value, default_framerate))

    def sizescale(self, value, default_scale = 80):
        return value * (default_scale / self.scale)


class World:
    def __init__(self, game):
        self.game = game
        self.time = datetime.datetime.now().replace(hour=12, minute = 0, second=0, microsecond=0)
        self.map_size = 1
        self.create_board()
        self.tile_size = Config().get_tile_size()
        self.size = [self.width(), self.height()]
        self.quest = Quest(0, 10, "Соберите монеты")
        self.create_npc()
        
    def create_board(self):
        board = []
        for row in range(0, int((self.game.config.get()['size_y'] // self.game.tiles.Tiles.absolute_size + 1) * self.map_size)): # y
            board.append([])
            for tile in range(0, int((self.game.config.get()['size_x'] // self.game.tiles.Tiles.absolute_size + 1) * self.map_size)): # x
                board[row] += [self.game.tiles.Grass([tile - (self.game.config.get()['size_x'] // self.game.tiles.Tiles.absolute_size + 1) * (self.map_size // 2), row - (self.game.config.get()['size_y'] // self.game.tiles.Tiles.absolute_size + 1) * (self.map_size // 2)])]
        self.board = board
    
    def create_npc(self):
        # self.game.npc.Wizard([self.game.width() * 0.25, self.game.get_center()[1]], self.game)
        # self.game.npc.Wizard([self.game.width() * 0.75, self.game.get_center()[1]], self.game)
        # self.game.npc.Male([self.game.get_center()[0], self.game.get_center()[1] * 0.5], self.game)
        pass
    
    def create_coins(self, num):
        for _ in range(num):
            Coin([
                self.board[0][0].pos[0] + random.randint(self.width() * 0.1, self.width() * 0.9),
                self.board[0][0].pos[1] + random.randint(self.height() * 0.1, self.height() * 0.9)
                ],
                self.game
                )
    
    def width(self):
        return (len(self.board[0])) * self.game.config.get_tile_size()
    
    def height(self):
        return (len(self.board)) * self.game.config.get_tile_size()
    
    def get_center(self): # от начала карты
        return (abs((self.width()) / 2), abs(self.height()) / 2)


class ActiveWindow:
    def __init__(self, window, windows):
        self.current_window = window
        self.game_window = windows[1]
        self.menu_window = windows[0]

    def show(self, screen):
        self.current_window.display(screen)

    def set(self, window):
        self.current_window = window
    
    def start_play(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.set(self.game_window)
    
    def check_game_quit(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.set(self.menu_window)
            return True
        return False
    
    def check_quit(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return True
    
    @property
    def __class__(self):
        return self.current_window.__class__


class EventReaction:
    def __init__(self, game, night_layer):
        self.running = True
        self.iteration = 0
        self.increase_time_speed = (1 // game.timescale(0.1))
        self.night_layer_change_speed = self.increase_time_speed * 5
        self.game = game
        self.game.night_layer = night_layer
        self.night_layer = night_layer
        self.night_layer_change()

    def react(self, events, active_window):
        if active_window.__class__ == Game:
            self.iteration += 1
            self.iteration %= self.game.timescale_int(1000000000)
            
            if self.iteration % self.increase_time_speed == 0:
                self.increase_time()
                if self.iteration % self.night_layer_change_speed == 0:
                    self.night_layer_change()
            
            for event in events:
                if active_window.check_game_quit(event):
                    events = []
                    break
                self.player_move(event)
        
            if any([self.game.player.direction_x, self.game.player.direction_y]) != 0:
                self.game.player.move((self.game.player.direction_x, self.game.player.direction_y), self.iteration)
                self.game.camera.set_center(self.game.player.rect.center)
                
            for npc in self.game.npc.NPC.all_npc:
                if self.iteration % self.game.timescale_int(npc.move_itaration) >= 1:
                    npc.move([npc.vx, npc.vy], self.iteration)
                else:
                    npc.vx, npc.vy = (random.random() - 0.5) * 2, (random.random() - 0.5) * 2
                    npc.move_itaration = random.randrange(50, 250)
            
            if self.game.world.quest.goal == self.game.world.quest.current_score:
                self.running = False
                    
        if active_window.__class__ == Menu:
            for event in events:
                self.running = False if active_window.check_quit(event) else True
                active_window.start_play(event)
    
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


class Quest:
    def __init__(self, current_score, goal, description):
        self.current_score = current_score
        self.goal = goal
        self.description = description
    
    def increase(self, points=1):
        if self.current_score < self.goal:
            self.current_score += points
    
    def completed(self):
        if self.current_score == self.goal:
            return True
        return False
    
    def get_current_score(self):
        return self.current_score
    
    def get_goal(self):
        return self.goal
    
    def get_description(self):
        return self.description
    
    def get_status(self):
        return f"{self.description}: {self.current_score}/{self.goal}"


class Objects(pygame.sprite.Sprite):
    all_objects = pygame.sprite.Group()
    
    def __init__(self, pos, game, is_stackable=False, is_placed=True):
        super().__init__(self.all_objects)
        self.is_stackable = is_stackable
        self.is_placed = is_placed
        self.game = game
        self.rect = self.image.get_rect()
        self.rect.midtop = pos
        
    def update(self, camera_pos): # отступ от края с учетом позиции камеры
        self.rect.x = self.rect.x - camera_pos[0]
        self.rect.centery = self.rect.centery - camera_pos[1]
        
        if self.__class__  == Coin:
            if pygame.sprite.collide_rect(self.game.player, self):
                self.game.world.quest.increase()
                self.kill()
                print(self.quest.get_status())    

    def place(self, pos):
        self.rect.x = self.rect.center[0] - pos[0]
        self.rect.centery = self.rect.center[1] - pos[1]

    def get_pos(self):
        return self.pos


class Coin(Objects):
    image = scale_image(load_image("sprites\\objects\\tiles\\coin.png", ), size=(Game.config.get_tile_size() * 0.5, Game.config.get_tile_size() * 0.5))
    all_coins = pygame.sprite.Group()
    
    def __init__(self, pos, game):
        super().__init__(pos, game)
        self.quest = game.world.quest
        self.all_coins.add(self)


class UI(pygame.sprite.Sprite):
    all_ui = pygame.sprite.Group()
    
    def __init__(self, game):
        super().__init__(self.all_ui)
        self.game = game
    
    def display_quest(self, screen):
        font = pygame.font.Font(None, 50)
        text = font.render(self.game.world.quest.get_status(), True, (255, 172, 55))
        text_x = self.game.width() - text.get_width() * 1.1
        text_y = self.game.height() - text.get_height() * 1.1
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
    
    def update(self):
        self.display_quest()
        

class Camera:
    all_sprites = pygame.sprite.Group()
    colliding_sprites = pygame.sprite.Group()
    cfg = Config()
    
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self.all_sprites)
        self.game = game
        self.player = game.player
        self.all_sprites.add(self.game.tiles.Tiles.all_tiles, Objects.all_objects, self.game.npc.NPC.all_npc, self.player.player_sprite, UI.all_ui)
        self.colliding_sprites.add(Objects.all_objects, self.game.npc.NPC.all_npc, self.player.player_sprite)
        self.colliding_sprites.remove(Coin.all_coins)
        self.pos = [0, 0]
        self.update(self.pos)
        
        for tile in self.game.tiles.Tiles.all_tiles:
            tile.place(self.pos)
    
    def update(self, pos): # обновление позиции относительно камеры
        self.all_sprites.update(pos)
  
    def set(self, pos):
        self.pos = pos
        self.update(self.pos)

    def set_center(self, pos):
        self.pos[0] = pos[0] - self.game.get_center()[0]
        self.pos[1] = pos[1] - self.game.get_center()[1]
        self.update(self.pos)

    def draw(self, screen):
        self.all_sprites.draw(screen)
