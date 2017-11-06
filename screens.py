import shelve
import asyncio
from random import randint
import pygame
import sys
import math
from pygame.rect import Rect
from assets import Assets
from async import AsyncTask
from colors import Colors
from styles import TextViewStyle, EditTextStyle, TextButtonStyle
from ui import TextView, EditText, Align, Palette, TextButton, LoadingView
from settings import Settings as Setts
from constants import Constants as Consts


class Context:
    def __init__(self, game, screen, firebase, auth):
        self.game = game
        self.screen = screen
        self.firebase = firebase
        self.auth = auth
        self.user = None
        self.loop = asyncio.get_event_loop()


class Screen:
    def __init__(self, context):
        self.context = context
        self.widgets = []
        self.init_widgets()
        self.is_clicked = False
        self.last_mouse_event = -1
        self.last_mouse_pos = (-1, -1)

    def init_widgets(self):
        pass

    def process_events(self, e):
        if e.type == pygame.QUIT:
            sys.exit()
        elif (e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.MOUSEBUTTONUP) and e.button == 1:
            pos = pygame.mouse.get_pos()
            self.is_clicked = e.type == pygame.MOUSEBUTTONUP and self.last_mouse_event == pygame.MOUSEBUTTONDOWN and \
                              self.last_mouse_pos[0] == pos[0] and self.last_mouse_pos[1] == pos[1]
            print(self.is_clicked)
        if self.is_clicked:
            for w in self.widgets:
                if w.hit(pos[0], pos[1]):
                    break
        self.last_mouse_event = e

    def update(self, delta):
        for w in self.widgets:
            w.update(delta)

    def draw(self):
        self.draw_bg(self.context.screen)
        for w in self.widgets:
            w.draw(self.context.screen)
        pygame.display.flip()

    def draw_bg(self, screen):
        self.context.screen.fill(Colors.white)


class LoginScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.edit_text_flag = False
        self.selected_edit_text = -1
        self.creds = self.load_credentials()
        self.login_task = None
        if self.creds[0] is not None:
            self.login_task = AsyncTask(self.login, self.creds)
            self.login_task.execute()

    def login(self, credentials):
        self.widgets[4].enabled = True
        self.widgets[2].is_editable = False
        self.widgets[3].is_editable = False
        email = credentials[0]
        password = credentials[1]
        try:
            self.context.user = self.context.auth.sign_in_with_email_and_password(email, password)
        except:
            self.context.user = self.context.auth.create_user_with_email_and_password(email, password)
            self.widgets[4].enabled = False
            self.widgets[2].is_editable = True
            self.widgets[3].is_editable = True
            return
        self.save_credentials(email, password)
        # self.initttt()
        self.context.game.set_screen('game')

    def save_credentials(self, email, password):
        file = shelve.open('player.data')
        file['email'] = email
        file['password'] = password
        file.close()

    def load_credentials(self):
        file = shelve.open('player.data')
        email = None
        password = None
        if 'email' in file:
            email = file['email']
            password = file['password']
        file.close()
        return email, password

    def init_widgets(self):
        style_regular = TextViewStyle(Assets.font_regular, Colors.black, Colors.white, Align.center)
        style_logo = TextViewStyle(Assets.font_logo, Colors.black, None, Align.center)
        style_edit_text = EditTextStyle(Assets.font_regular, Colors.black, Colors.grey, Colors.white, Align.center)
        size = Assets.font_regular.size("Mail.ru's")
        self.widgets.append(TextView("Mail.ru's", (
            Setts.screen_width / 2 - size[0] / 2, .30 * Setts.screen_height - size[1] / 2), style_regular))
        size = Assets.font_logo.size("Battlegrounds")
        self.widgets.append(TextView("Battlegrounds",
                                     (Setts.screen_width / 2 - size[0] / 2, .40 * Setts.screen_height - size[1] / 2),
                                     style_logo))
        size = Assets.font_regular.size("email")
        self.widgets.append(EditText("email", (Setts.screen_width / 2 - size[0] / 2, .5 * Setts.screen_height),
                                     style_edit_text))
        size = Assets.font_regular.size("password")
        self.widgets.append(EditText("password", (Setts.screen_width / 2 - size[0] / 2, .6 * Setts.screen_height),
                                     style_edit_text, True))
        """size = Assets.font_regular.size("Login")
        self.widgets.append(
            TextButton("Login", (Setts.screen_width / 2 - (size[0] + 10) / 2, .73 * Setts.screen_height),
                       style_button))"""
        self.widgets.append(LoadingView((Setts.screen_width / 2 - Consts.frame_width / 2, .73 * Setts.screen_height)))

    def switch_edit_texts(self):
        if self.selected_edit_text != -1:
            i = 2 if self.selected_edit_text == 3 else 3
            j = 3 if self.selected_edit_text == 3 else 2
            self.selected_edit_text = i
            self.widgets[j].lose_focus()
            self.widgets[i].hit(self.widgets[i].x, self.widgets[i].y)

    def process_events(self, e):
        if self.edit_text_flag:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.widgets[self.selected_edit_text].move_cursor(-1)
                elif e.key == pygame.K_RIGHT:
                    self.widgets[self.selected_edit_text].move_cursor(1)
                elif e.key == pygame.K_BACKSPACE:
                    self.widgets[self.selected_edit_text].delete_symbol()
                elif e.key == pygame.K_TAB:
                    self.switch_edit_texts()
                elif e.key == pygame.K_RETURN:
                    if self.widgets[3].get_text() == '':
                        self.switch_edit_texts()
                    else:
                        self.creds = (self.widgets[2].get_text(), self.widgets[3].get_text())
                        self.login_task = AsyncTask(self.login, self.creds)
                        self.login_task.execute()
                else:
                    self.widgets[self.selected_edit_text].append_text(e.unicode)
        if e.type == pygame.QUIT:
            sys.exit()
        else:
            pos = pygame.mouse.get_pos()
            self.is_clicked = e.type == pygame.MOUSEBUTTONUP and self.last_mouse_event.type == pygame.MOUSEBUTTONDOWN and \
                              e.button == 1 and self.last_mouse_pos[0] == pos[0] and self.last_mouse_pos[1] == pos[1]
            self.last_mouse_pos = pos
            self.last_mouse_event = e
        if self.is_clicked:
            i = 0
            for w in self.widgets:
                res = w.hit(pos[0], pos[1])
                if res[0]:
                    if res[1] == 'edit':
                        self.edit_text_flag = True
                        self.selected_edit_text = i
                        if self.selected_edit_text == 2:
                            self.widgets[3].lose_focus()
                    else:
                        self.unfocus_edit_text()
                    return
                i += 1
            self.unfocus_edit_text()

    def unfocus_edit_text(self):
        self.edit_text_flag = False
        self.selected_edit_text = -1

    def initttt(self):
        pixels = self.context.firebase.database()
        for j in range(0, 1000):
            pixels.child('pixels-test').child(str(j)).set(
                {
                    'color': [255, 255, 255]
                }, self.context.user['idToken'])


class GameScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.canvas = pygame.Surface(
            [Consts.game_field_width * Consts.pixel_size,
             Consts.game_field_height * Consts.pixel_size]).convert_alpha()
        self.canvas.fill((255, 255, 255))
        self.camera = Rect(0, 0, Consts.game_field_width * Consts.pixel_size,
                           Consts.game_field_height * Consts.pixel_size)
        self.is_lmb_held = False
        self.camera_x = 0
        self.camera_y = 0
        self.count = 0
        self.passed_time = 0
        self.db = self.context.firebase.database()
        self.pixels_stream = self.db.child('pixels-test').stream(self.receive_pixel, self.get_token())
        self.suggestion = None
        self.target = Target()
        self.load_game_field()

    def init_widgets(self):
        self.widgets.append(Palette(Colors.transparent_white))
        self.palette = self.widgets[0]

    def draw_bg(self, screen):
        camera_canvas = pygame.Surface((self.camera.w, self.camera.h))
        camera_canvas.fill(Colors.red)
        camera_canvas.blit(self.canvas, (0, 0), Rect(self.camera_x, self.camera_y, self.camera.w, self.camera.h))
        camera_canvas = pygame.transform.scale(camera_canvas, (Setts.screen_width, Setts.screen_height))
        screen.blit(camera_canvas, (0, 0))

    def draw_suggestion(self):
        if self.palette.selected != -1:
            if self.target.different and self.target.prev_color is not None:
                self.target.different = False
                pygame.draw.rect(self.canvas, self.target.prev_color,
                                 Rect(self.target.prev_dest[0], self.target.prev_dest[1], 1, 1))
            pygame.draw.rect(self.canvas, self.target.target_color,
                             Rect(self.target.dest[0], self.target.dest[1], 1, 1))

    def draw(self):
        super().draw()
        self.draw_suggestion()

    def load_game_field(self):
        pixels = self.db.child('pixels-test').get(self.get_token()).val()
        for j in range(0, 20):
            for i in range(0, 50):
                colors = pixels[i + Consts.game_field_width * j]['color']
                self.canvas.set_at((i, j), colors)

    def get_token(self):
        return self.context.user['idToken']

    def receive_pixel(self, pixel):
        self.count += 1
        if self.count > 1:
            number = int(pixel['path'][1:])
            x = number % Consts.game_field_width
            y = int((number - x) / Consts.game_field_height)
            self.canvas.set_at((x, y), pixel['data']['color'])

    def conquer_pixel(self):
        x = int(self.coords[0] * (self.camera.w / Setts.screen_width) + self.camera.x)
        y = int(self.coords[1] * (self.camera.h / Setts.screen_height) + self.camera.y)
        colors = Colors.game[self.palette.selected]
        self.send_pixel((x, y), colors)

    def send_pixel(self, dest, colors):
        self.db.child('pixels-test').child(str(dest[0] + dest[1] * Consts.game_field_width)).update(
            {
                "color": colors
            }, self.get_token())

    def update_user_token(self, delta):
        self.passed_time += delta
        if self.passed_time > 55 * 60 * 1000:  # update token every 50 minutes
            self.context.auth.refresh(self.context.user['refreshToken'])
            self.passed_time = 0

    def update(self, delta):
        self.update_user_token(delta)
        super().update(delta)

    def inflate_camera(self, offset_x, offset_y):
        self.camera.inflate_ip(offset_x, offset_y)
        self.camera_x -= offset_x / 2
        self.camera_y -= offset_y / 2

    def process_events(self, e):
        if e.type == pygame.QUIT:
            sys.exit()
        elif e.type == pygame.MOUSEBUTTONDOWN:
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
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                self.is_lmb_held = False
        self.check_click(e)
        if self.is_clicked:
            pos = pygame.mouse.get_pos()
            flag = False
            for w in self.widgets:
                flag = w.hit(pos[0], pos[1]) or False
            if not flag[0] and self.palette.selected != -1:
                self.target.prev_dest = None
                self.conquer_pixel()
            self.palette.selected = flag[2] if flag[0] and flag[1] == 'palette' else -1
        if self.is_lmb_held:
            self.move_field()
        self.check_fill()

    def check_click(self, e):
        pos = pygame.mouse.get_pos()
        self.is_clicked = e.type == pygame.MOUSEBUTTONUP and self.last_mouse_event.type == pygame.MOUSEBUTTONDOWN and \
                          e.button == 1 and math.fabs(self.last_mouse_pos[0] - pos[0]) <= 1 and \
                          math.fabs(self.last_mouse_pos[1] - pos[1]) <= 1
        self.last_mouse_pos = pos
        self.last_mouse_event = e

    def check_fill(self):
        if self.palette.selected != -1:
            pos = pygame.mouse.get_pos()
            x = int(pos[0] * (self.camera.w / Setts.screen_width) + self.camera.x)
            y = int(pos[1] * (self.camera.h / Setts.screen_height) + self.camera.y)
            if 0 <= x <= Consts.game_field_width and 0 <= y <= Consts.game_field_height:
                self.target.commit((x, y), Colors.game[self.palette.selected], self.canvas.get_at((x, y)))

    def move_field(self):
        curr_coords = pygame.mouse.get_pos()
        self.camera_x += (self.coords[0] - curr_coords[0]) * (self.camera.w / Setts.screen_width)
        self.camera_y += (self.coords[1] - curr_coords[1]) * (self.camera.h / Setts.screen_height)
        self.camera.__setattr__('x', self.camera_x)
        self.camera.__setattr__('y', self.camera_y)
        self.coords = curr_coords


class Target:
    def __init__(self):
        self.dest = (-1, -1)
        self.target_color = None
        self.curr_color = None
        self.prev_dest = None
        self.prev_color = None
        self.different = False

    def commit(self, dest, target_color, curr_color):
        if self.dest[0] != dest[0] or self.dest[1] != dest[1]:
            self.prev_dest = self.dest
            self.prev_color = self.curr_color
            self.dest = dest
            self.target_color = target_color
            self.curr_color = curr_color
            self.different = True
