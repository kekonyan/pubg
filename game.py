from enum import Enum

import pygame
import sys
import pyrebase
from random import randint
from pygame.rect import Rect
from assets import Assets
from constants import Constants as Consts
from settings import Settings as Setts
from ui import TextView


class State(Enum):
    LOGIN = 1
    GAME = 2


class Game:
    def __init__(self):
        pygame.init()

        Consts()
        Assets()
        Setts()

        self.state = State.GAME
        self.screen = pygame.display.set_mode((Setts.screen_width, Setts.screen_height))
        pygame.display.set_caption(Setts.display_caption)
        self.screen.fill(Setts.bg_color)

        self.canvas = pygame.Surface(
            [Consts.game_field_width * Consts.pixel_size,
             Consts.game_field_height * Consts.pixel_size]).convert_alpha()
        self.canvas.fill((255, 255, 255))
        self.camera = Rect(0, 0, Consts.game_field_width * Consts.pixel_size, Consts.game_field_height * Consts.pixel_size)
        self.is_lmb_held = False
        self.camera_x = 0
        self.camera_y = 0
        self.count = 0
        self.passed_time = 0
        self.clock = pygame.time.Clock()

        # self.testTV = TextView(500, 300, (50, 120, 200), 'dont you feel sorry for stickers', (0, 240, 240),
        #                       (50, 120, 200), (400, 200))

    def init_pyrebase(self):
        config = {
            "apiKey": "AIzaSyCtCNdjjhu3YRmfABltpeJC2nq5OXTlgxc",
            "authDomain": "pixel-battlegrounds.firebaseapp.com",
            "databaseURL": "https://pixel-battlegrounds.firebaseio.com",
            "projectId": "pixel-battlegrounds",
            "storageBucket": "pixel-battlegrounds.appspot.com",
            "messagingSenderId": "704655328627"
        }

        firebase = pyrebase.initialize_app(config)

        self.auth = firebase.auth()

        # if auth.current_user == None:
        #    user=auth.create_user_with_email_and_password("constantinopolskaya228@gmail.com", "chelsea17")
        # else:
        self.user = self.auth.sign_in_with_email_and_password("constantinopolskaya228@gmail.com", "chelsea17")

        self.db = firebase.database()
        pixels = self.db.get(self.get_token()).val()
        for i in range(0, Consts.game_field_width):
            for j in range(0, Consts.game_field_height):
                colors = pixels[i][j]['color']
                self.canvas.set_at((i, j), colors)
        self.pixels_stream = self.db.stream(self.receive_pixel, self.get_token())

    def receive_pixel(self, pixel):
        self.count += 1
        if self.count > 1:
            data = list(pixel['data'].keys())[0].split('/')
            dest = (int(data[0]), int(data[1]))
            self.canvas.set_at(dest, list(pixel['data'].values())[0]['color'])

    def get_token(self):
        return self.user['idToken']

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.is_lmb_held = True
                    self.coords = pygame.mouse.get_pos()
                if e.button == 4:  # zoom in
                    offset_x = -self.camera.w * Consts.scroll_amount
                    offset_y = -self.camera.h * Consts.scroll_amount
                    if self.camera.w + offset_x <= Consts.upscale_limit:
                        offset_x = 0
                        offset_y = 0
                    self.inflate_camera(offset_x, offset_y)
                elif e.button == 5:  # zoom out
                    offset_x = self.camera.w * Consts.scroll_amount
                    offset_y = self.camera.h * Consts.scroll_amount
                    if self.camera.w + offset_x > Consts.downscale_limit:
                        offset_x = 0
                        offset_y = 0
                    self.inflate_camera(offset_x, offset_y)
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    self.conquer_pixel()
                    self.is_lmb_held = False

        if self.is_lmb_held:
            curr_coords = pygame.mouse.get_pos()
            self.camera_x += (self.coords[0] - curr_coords[0]) * (self.camera.w / Setts.screen_width)
            self.camera_y += (self.coords[1] - curr_coords[1]) * (self.camera.h / Setts.screen_height)
            self.camera.__setattr__('x', self.camera_x)
            self.camera.__setattr__('y', self.camera_y)
            self.coords = curr_coords

    def inflate_camera(self, offset_x, offset_y):
        self.camera.inflate_ip(offset_x, offset_y)
        self.camera_x -= offset_x / 2
        self.camera_y -= offset_y / 2

    def conquer_pixel(self):
        x = int(self.coords[0] * (self.camera.w / Setts.screen_width) + self.camera.x)
        y = int(self.coords[1] * (self.camera.h / Setts.screen_height) + self.camera.y)
        colors = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.send_pixel((x, y), colors)

    def send_pixel(self, dest, colors):
        self.db.update({
            str(dest[0]) + '/' + str(dest[1]) + '/': {
                "color": colors
            }
        }, self.get_token())

    def draw(self):
        self.screen.fill((255, 255, 255))
        if self.state == State.GAME:
            camera_canvas = pygame.Surface((self.camera.w, self.camera.h))
            camera_canvas.blit(self.canvas, (0, 0), Rect(self.camera_x, self.camera_y, self.camera.w, self.camera.h))
            camera_canvas = pygame.transform.scale(camera_canvas, (Setts.screen_width, Setts.screen_height))
            self.screen.blit(camera_canvas, (0, 0))
        elif self.state == State.LOGIN:
            self.testTV.draw(self.screen)

        pygame.display.flip()

    def update_user_token(self):
        self.passed_time += self.clock.tick()
        if self.passed_time > 55 * 60 * 1000:  # update token every 55 minutes
            self.auth.refresh(self.user['refreshToken'])
            self.passed_time = 0

    def run(self):
        self.init_pyrebase()
        while 1:
            self.update_user_token()
            self.process_events()
            self.draw()


game = Game()
game.run()