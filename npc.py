import random
import functions
import objects
import pygame

  
class NPC(pygame.sprite.Sprite):
    all_npc = pygame.sprite.Group()
    cfg = objects.Config()
    mixer_initialized = False
    try:
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()
        mixer_initialized = True
    except:
        pass
    
    def __init__(self, name, pos, game, health, image_src, weight=55):
        self.size_per_tile = 0.9
        self.frames = functions.scale_image(objects.AnimatedSprite.cut_sheet(
            functions.load_image(image_src), 3, 4), 
            size=(
                int(self.cfg.get_tile_size() * self.size_per_tile),
                int(self.cfg.get_tile_size() * self.size_per_tile)
            ))
        self.image = self.frames[1]
        self.rect = self.image.get_rect()
        if name != Player.__name__:
            super().__init__(self.all_npc)
            self.vx = 0
            self.vy = 0
            self.move_itaration = random.randrange(50, 250)
            self.rect.center = pos
        else:
            super().__init__(Player.player_sprite)
        
        self.name = name
        self.max_health = health
        self.health = health
        self.weight = weight
        self.game = game
        self.default_velocity = game.sizescale(0.1)
        self.velocity = self.get_velocity()
        self.animation_speed = game.timescale_int(24) # lower - faster
        self.previous_animation_num = None
        
        if self.mixer_initialized:
            self.walking_sound = pygame.mixer.Sound('sounds\\walking.wav')
            self.walking_sound.set_volume(0.12)

    def set_pos(self, pos):
        self.rect.center = pos

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
        self.COLLIDE_BORDERS = True
        animation_num = int(iteration // self.game.timescale(self.animation_speed) % 3)
        moved = False
        
        if abs(offset[0]) == abs(offset[1]) != 0:
            if offset[0] != 0:
                moved = self.x_move(offset, diagonal=True)
            if offset[1] != 0:
                moved = self.y_move(offset, diagonal=True)
        else:
            if offset[0] != 0:
                moved = self.x_move(offset)
            if offset[1] != 0:
                moved = self.y_move(offset)
        
        if offset[0] != 0 and moved:
            if offset[0] > 0:
                self.image = self.frames[6 + animation_num]
            if offset[0] < 0:
                self.image = self.frames[3 + animation_num]
        elif offset[1] != 0 and moved:
            if offset[1] > 0:
                self.image = self.frames[9 + animation_num]
            if offset[1] < 0:
                self.image = self.frames[animation_num]
        
        if offset[0] == offset[1] == 0:
            if self.mixer_initialized:
                self.walking_sound.stop()
        
        if self.previous_animation_num != animation_num and moved:
            try:
                self.walking_sound.stop()
            except:
                pass
            if self.mixer_initialized:
                if self.__class__ != Player:
                    self.walking_sound.set_volume(max(0, 1 / (abs(self.game.player.rect.centerx - self.rect.centerx) ** 2 + abs(self.game.player.rect.centery - self.rect.centery) ** 2) ** 0.5) * 50)
                
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
    
    def x_move(self, offset, diagonal=False):
        self.rect.centerx += self.game.sizescale(offset[0]) * (0.75 if diagonal else 1) * self.get_velocity()
        
        objects.Camera.colliding_sprites.remove(self)
        if not pygame.sprite.spritecollide(self, objects.Camera.colliding_sprites, False):
            if self.COLLIDE_BORDERS:
                if self.game.world.board[0][0].rect.left < self.rect.left and self.rect.right < self.game.world.board[-1][-1].rect.right:
                    objects.Camera.colliding_sprites.add(self)
                    return True
                else:
                    self.rect.centerx -= self.game.sizescale(offset[0]) * self.get_velocity()
                    objects.Camera.colliding_sprites.add(self)
                    return False
            objects.Camera.colliding_sprites.add(self)
            return True
        else:
            self.rect.centerx -= self.game.sizescale(offset[0]) * self.get_velocity()
            objects.Camera.colliding_sprites.add(self)
            return False
    
    def y_move(self, offset, diagonal=False):
        self.rect.centery -= self.game.sizescale(offset[1]) * (0.75 if diagonal else 1) * self.get_velocity()
        
        objects.Camera.colliding_sprites.remove(self)
        if not pygame.sprite.spritecollide(self, objects.Camera.colliding_sprites, False):
            if self.COLLIDE_BORDERS:
                if self.game.world.board[0][0].rect.top < self.rect.top and self.rect.bottom < self.game.world.board[-1][-1].rect.bottom:
                    objects.Camera.colliding_sprites.add(self)
                    return True
                else:
                    self.rect.centery += self.game.sizescale(offset[1]) * self.get_velocity()
                    objects.Camera.colliding_sprites.add(self)
                    return False
            objects.Camera.colliding_sprites.add(self)
            return True
        else:
            self.rect.centery += self.game.sizescale(offset[1]) * self.get_velocity()
            return False
    
    def update(self, camera_pos): # отступ от края с учетом позиции камеры
        self.rect.centerx = self.rect.centerx - camera_pos[0]
        self.rect.centery = self.rect.centery - camera_pos[1]
    
    def __str__(self):
        return f"{self.__class__}_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()
  

class Player(NPC):
    player_sprite = pygame.sprite.GroupSingle()
    
    def __init__(self, player_name, game, health=100, weight=50):
        NPC.__init__(self, player_name, game.get_center(), game, health, "sprites\\objects\\Characters\\female.png", weight)
        self.rect.center = self.game.get_center()
        self.default_velocity = game.sizescale(0.2)
        self.is_moving = False
        self.direction_x = 0
        self.direction_y = 0

    def __str__(self):
        return f"{self.__class__}_{self.name}: ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self):
        return self.__str__()


class Male(NPC):
    def __init__(self, pos, game):
        super().__init__(self.__class__, pos, game, health=100, image_src="sprites\\objects\\Characters\\NPC\\male.png")


class Wizard(NPC):
    def __init__(self, pos, game):
        super().__init__(self.__class__, pos, game, health=100, image_src="sprites\\objects\\Characters\\NPC\\wizard.png")
