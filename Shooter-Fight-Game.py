#shooter Fight Game 2021

import pygame
from pygame import mixer
import os
import random
import csv

mixer.init()
pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = int(SCREEN_WIDTH + 0.9)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SHOOTER SCROLLING GAME")

#gravity
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
MAX_LEVELS = 5
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

clock = pygame.time.Clock()
FPS = 60
#load music and sounds
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 500)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)

pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()

#store tile  in list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#images
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

#granade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

#item boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load(
    'img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'health': health_box_img,
    'ammo': ammo_box_img,
    'Grenade': grenade_box_img
}
#bg colors
BG = (69, 139, 116)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
#font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img,
                    ((x * width) - bg_scroll * 0.6,
                     SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.7,
                                SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8,
                                SCREEN_HEIGHT - pine2_img.get_height() - 150))


def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


#define  player action variables'
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


class soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.vel_y = 0
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific varibles
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.indling_counter = 0

        animation_types = ['idle', 'Run', 'Jump', 'Death']

        for animation in animation_types:
            #reset tempory list of images
            temp_list = []
            #count the number of filesin folder

            num_of_frames = len(
                os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'img/{self.char_type}/{animation}/{i}.png').convert_alpha(
                    )
                img = pygame.transform.scale(img, (int(
                    img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #pudate cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #present movement varaiables
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -20
            self.jump = False
            self.in_air = True


#   apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check  for collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width,
                                   self.height):
                dx = 0
                #if the ai has hit a wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            #cheack for collision for y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,
                                   self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check if going off  the edges of the screen:
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #update rectangle  positions
        self.rect.x += dx
        self.rect.y += dy

        #update scroll base on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll <
                (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (
                    self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(
                self.rect.centerx +
                (0.80 * self.rect.size[0] * self.direction), self.rect.centery,
                self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.indling_counter = 50
            #check if ai near the player
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx +
                                          75 * self.direction,
                                          self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.indling_counter -= 1
                    if self.indling_counter <= 0:
                        self.idling = False

        #scroll
        self.rect.x += screen_scroll

    def update_animation(self):

        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        #check the ebough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation run out then reset
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if the new
        if new_action != self.action:
            self.action = new_action
            #update the animation setings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),
                    self.rect)
        # pygame.draw.rect(screen ,RED, self.rect, 1)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #itrete though each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE,
                                                y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = soldier('player', x * TILE_SIZE,
                                         y * TILE_SIZE, 1.65, 5, 100, 100)
                        health_bar = HealthBar(10, 10, player.health,
                                               player.health)
                    elif tile == 16:
                        enemy = soldier('enemy', x * TILE_SIZE, y * TILE_SIZE,
                                        1.65, 2, 20, 100)
                        enemy_group.add(enemy)
                    elif tile == 17:  #ammo box
                        item_box = ItemBox('ammo', x * TILE_SIZE,
                                           y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  #grenade box
                        item_box = ItemBox(
                            'Grenade',
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                        )
                        item_box_group.add(item_box)
                    elif tile == 19:  #health  box
                        item_box = ItemBox('health', x * TILE_SIZE,
                                           y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2,
                            y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2,
                            y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2,
                            y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2,
                            y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        #calculate health rattio
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) - screen_scroll

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 110:
            self.kill()

        #check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #checking collison with characters:
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 2
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 10
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 50
        self.vel_y = -13
        self.speed = 8
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width,
                                   self.height):
                self.direction *= -1
                dx = self.direction * self.speed

            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width,
                                   self.height):
                self.speed = 0
                #cheack for collision for y
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += (self.direction * self.speed)

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        #update
        self.rect.x += dx + screen_scroll  #don't chase money chase your happiense it your responsebility
        self.rect.y += dy

        #countdownn timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
              abs(self.rect.centerx - player.rect.centery) < TILE_SIZE * 2 :
                player.health -= 20

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                 abs(self.rect.centerx - enemy.rect.centery) < TILE_SIZE * 2 :
                    enemy.health -= 20


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(
                f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(
                img,
                (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        #update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete than delete the explsion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1:
            pygame.draw.rect(
                screen, self.colour,
                (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        if self.direction == 2:
            pygame.draw.rect(screen, self.colour,
                             (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


intro_fade = ScreenFade(3, BLACK, 7)
death_fade = ScreenFade(2, PINK, 4)

#button class

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

player = soldier('player', 100000, 200, 1.65, 2, 100, 100)
health_bar = HealthBar(10, 10, player.health, player.health)

enemy = soldier('enemy', 500, 200, 1.65, 2, 100, 100)
# enemy2 = soldier('enemy', 250, 200, 1.65, 1, 100, 100)
enemy_group.add(enemy)
# enemy_group.add(enemy2)

#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

x = 200
y = 200

run = True
while run:
    clock.tick(FPS)

    if start_game == False:
        screen.fill(BG)
    start_intro = True

    draw_bg()
    #drawing background
    world.draw()

    health_bar.draw(player.health)
    draw_text('AMMO:  ', font, WHITE, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_img, (90 + (x * 10), 40))

    draw_text('GRENADES:  ', font, WHITE, 15, 60)
    for x in range(player.grenades):
        screen.blit(grenade_img, (135 + (x * 15), 50))

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)

    #update player action
    if player.alive:
        #shoot bullets
        if shoot:
            player.shoot()
        #throw granade
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.3 * player.rect.size[0] * player.direction),\
                           player.rect.top, player.direction)
            grenade_group.add(grenade)
            #grenade reduce
            grenade_thrown = True
            player.grenades -= 1

        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)
        screen_scroll, level_complete = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll
        if level_complete:
            level += 1
            bg_scroll = 0
            world_data = reset_level()
            if level <= MAX_LEVELS:
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

    else:
        screen_scroll = 0
        death_fade.fade()
        bg_scroll = 0
        world_data = reset_level()

        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
        world = World()
        player, health_bar = world.process_data(world_data)
    # player.move(moving_left, moving_right)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                moving_left = True
            if event.key == pygame.K_f:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_g:
                grenade = True
            if event.key == pygame.K_j and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_b:
                moving_left = False
            if event.key == pygame.K_f:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_g:
                grenade = False
                grenade_thrown = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

#Hope You Like It!

#if you think you can add more items and make this game more amazing then feel free to add
