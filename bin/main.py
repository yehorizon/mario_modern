# -*- coding: utf-8 -*-

import sys
import pygame
import time

import mario
import coinbox
import coin
import brick
import flower
import config
import tmx
import turtle
import powerup
from database import DataBase

FONT_NAME = "seguisym.ttf"
if not pygame.mixer: print('Warning, sound disabled')

class Profile(object, DataBase):
    def __init__(self):
        DataBase.__init__(self)

        # init started profile`s value
        self.username, self.rating, self.date = '', 0, 0
        self.options = {
            1: self.get_users,
            2: self.play,
            3: self.alert
        }
        self.basicMenu()

    def alert(self):
        print('hello MIPT =)')

    def basicMenu(self):
        self.opt_text = ("""Hello! Choose option..
                            1 - get all user data 
                            2 - play
                        Option:""")
        self.opt = int(input(self.opt_text))
        self.options[self.opt]()


    def get_users(self):
        data = {}
        users = DataBase.get_dataframe(self, **data)
        for user in users:

            id_ = user[0]
            name = user[1]
            rating = user[2]
            date = user[3]
            print("""id: %s | name: %s  | rating: %s | Last join: %s """
                  % (id_,name,rating,date))

        self.basicMenu()

    def play(self):

        self.username = str(input('Enter your username: '))
        time_ = time.time()
        data = {'username': self.username,
                'date':time_}
        try:
            user = (DataBase.get_user(self, **data) or
                    DataBase.append_user(self, **data))

            if user:
                self.rating = int(user[0][1])
            else:
                self.rating = 0

        except Exception as E:

            raise TypeError('Invalid base data')




class MarioGame(object):

    width = 1280
    height = 720
    game_over = False

    def __init__(self, Profile):
        self.pygame = pygame
        self.Profile = Profile

    def init(self):
        self.pygame.init()
        self.size = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = self.pygame.time.Clock()
        self.time_step = 0

        self.init_map('map.tmx', None, True)
        self.bg_color = config.SKY

    def init_map(self, map_file, new_pos, first_time):
        self.tilemap = tmx.load(map_file, self.screen.get_size())

        if first_time:
            # condition for first attempt
            self.sprites = tmx.SpriteLayer()
            start_cell = self.tilemap.layers['triggers'].find('player')[0]
            self.my_mario = mario.Mario((start_cell.px, start_cell.py), self.sprites)
        else:
            start_cell = self.tilemap.layers['triggers'].find(new_pos)[0]
        self.my_mario.rect.topleft = (start_cell.px, start_cell.py)

        self.coinboxs = tmx.SpriteLayer()
        for _coinbox in self.tilemap.layers['triggers'].find('coinbox'):
            box_type = getattr(coinbox, _coinbox.properties.get("type", "SECRET"))
            prize = None
            if _coinbox.properties.get("item"):
                prize = getattr(powerup, _coinbox.properties.get("item"))
            count = _coinbox.properties.get("count", 1)
            coinbox.CoinBox(self, (_coinbox.px, _coinbox.py), box_type, prize, count, self.coinboxs)

        self.bricks = tmx.SpriteLayer()
        for _brick in self.tilemap.layers['triggers'].find('brick'):
            brick.Brick(self, (_brick.px, _brick.py), self.bricks)

        self.coins = tmx.SpriteLayer()
        for _coin in self.tilemap.layers['triggers'].find('coin'):
            coin.Coin((_coin.px, _coin.py), self.coins)

        self.enemies = tmx.SpriteLayer()
        for _turtle in self.tilemap.layers['triggers'].find('turtle'):
            turtle.Turtle((_turtle.px, _turtle.py), self.enemies)
        for _flower in self.tilemap.layers['triggers'].find('flower'):
            color = getattr(flower, _flower.properties.get("color", "GREEN_FLOWER"))
            flower.Flower((_flower.px, _flower.py), color, self.enemies)

        self.powerups = tmx.SpriteLayer()
        # layer order: background, midground + sprites, foreground
        self.insert_layer(self.powerups, "powerups", 1)
        self.insert_layer(self.coins, "coins", 2)
        self.insert_layer(self.coinboxs, "coinboxs", 3)
        self.insert_layer(self.bricks, "bricks", 4)
        self.insert_layer(self.enemies, "enemies", 5)
        self.insert_layer(self.sprites, "sprites", 6)


    def insert_layer(self, sprites, layer_name, z_order):
        self.tilemap.layers.add_named(sprites, layer_name)
        self.tilemap.layers.remove(sprites)
        self.tilemap.layers.insert(z_order, sprites)

    def run(self):
        # main game loop
        while True:
            # 60 fps
            dt = self.clock.tick(60)
            self.time_step += 1
            # enumerate event
            for event in pygame.event.get():
                if event.type == pygame.QUIT \
                    or event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    sys.exit(0)
                # sprite handle event
                self.handle(event)

            self.update(dt)
            # re-draw screen
            self.draw(self.screen)

    def draw(self, screen):
        screen.fill(self.bg_color)
        if not self.game_over:
            for box in self.coinboxs:
                box.draw_coin(screen)
            self.tilemap.draw(screen)
            for brick in self.bricks:
                brick.draw_particles(screen)
            # debuggng
            #self.draw_debug(screen)
            self.draw_score_texts(screen)
            self.draw_profile_username(screen)
            if self.my_mario.state == "dying":
                self.draw_dying_screen(screen)
        else:
            self.draw_gameover_screen(screen)

        self.pygame.display.flip()

    def draw_debug(self, screen):
        pygame.draw.rect(screen,  config.WHITE, pygame.Rect(80, 396, 20, 14))

    def update(self, dt):
        # may be not the best practice ..
        if self.my_mario.state == "piped":
            next_map = self.my_mario.pipe_obj.properties.get("map")
            new_pos = self.my_mario.pipe_obj.properties.get("next")
            self.init_map(next_map + '.tmx', new_pos, False)
            if "underground" in next_map:
                self.bg_color = config.BLACK
            else:
                self.bg_color = config.SKY
            self.my_mario.state = "normal"

        self.tilemap.update(dt / 1000., self)


    def handle(self, event):
        # event handling
        self.my_mario.handle(event)

    def draw_profile_username(self, screen):
        if pygame.font:
            name_text = pygame.font.Font(FONT_NAME, 24).render('Name: '+ str(self.Profile.username), 1, (255, 255, 255))
            name_textpos = name_text.get_rect(left=10, top=50)
            self.screen.blit(name_text, name_textpos)


    def draw_score_texts(self, screen):
        # drawing score
        if pygame.font:
            lives_text = pygame.font.Font(FONT_NAME, 24).render("Mario x %s" % self.my_mario.lives, 1, (255, 255, 255))
            coins_text = pygame.font.Font(FONT_NAME, 24).render("Points x %s" % self.my_mario.collected_coins, 1, (255, 255, 255))
            previous_rating_text = pygame.font.Font(FONT_NAME, 24).render("Previous Rating x %s" % self.Profile.rating,
                                                                          1, (255, 255, 255)
                                                                          )
            prev_rate_textpos = previous_rating_text.get_rect(right=self.width-10, top=50)
            over_textpos = lives_text.get_rect(left=10, top=10)
            coins_textpos = coins_text.get_rect(right=self.width - 10, top=10)
            self.screen.blit(lives_text, over_textpos)
            self.screen.blit(coins_text, coins_textpos)
            self.screen.blit(previous_rating_text, prev_rate_textpos)
    

    def draw_gameover_screen(self, screen):
        screen.fill(config.BLACK)
        if pygame.font:
            over_text = pygame.font.Font(FONT_NAME, 36).render("Game over !!!", 1, (255, 255, 255))
            quit_text = pygame.font.Font(FONT_NAME, 24).render("Press 'q' to exit.", 1, (255, 255, 255))
            over_textpos = over_text.get_rect(centerx=self.width/2, centery=self.height/2 - 36)
            quit_textpos = quit_text.get_rect(centerx=self.width/2, centery=self.height/2)
            self.screen.blit(over_text, over_textpos)
            self.screen.blit(quit_text, quit_textpos)


    def draw_dying_screen(self, screen):
        screen.fill((128, 128, 128, 128), None, pygame.BLEND_RGBA_MULT)
        if pygame.font:
            font = pygame.font.Font(FONT_NAME, 24)
            dead_text = font.render("Your person is died.", 1, (255, 255, 255))
            again_text = font.render("Press ENTER for another one attempt !", 1, (255, 255, 255))
            dead_textpos = dead_text.get_rect(centerx=self.width/2, centery=self.height/2 - 36)
            again_textpos = again_text.get_rect(centerx=self.width/2, centery=self.height/2)
            self.screen.blit(dead_text, dead_textpos)
            self.screen.blit(again_text, again_textpos)

    def __del__(self):
        # uploaded collected coins into base data
        coins = self.my_mario.collected_coins
        username = self.Profile.username
        date = time.time()
        # choosing max of these current rating and old rating
        new_rating = max(self.Profile.rating, coins)
        data = {'username':username,
                'date':date,
                'rating':new_rating}
        self.Profile.user_commit(self, **data)


if __name__ == '__main__':
    # init game
    prof = Profile()

    g = MarioGame(prof)
    g.init()
    g.run()
