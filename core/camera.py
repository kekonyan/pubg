from pygame.rect import Rect

from util.constants import Constants


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.scale = Constants.DOWNSCALE_BOUND
        self.rect = Rect(0, 0, Constants.CANVAS_SIZE, Constants.CANVAS_SIZE)
        self.center_x = Constants.SCREEN_WIDTH / 2
        self.center_y = Constants.SCREEN_HEIGHT / 2
        self.fit_and_center()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def scale_by(self, amount):
        old_scale = self.scale
        self.scale += amount * self.scale
        self.scale = max(Constants.DOWNSCALE_BOUND, self.scale)
        self.scale = min(Constants.UPSCALE_BOUND, self.scale)
        # v = s(v−p)+p, s = amount, v - arbitrary point, p - fixed point
        scale = self.scale / old_scale
        self.x = scale * (self.x - self.center_x) + self.center_x
        self.y = scale * (self.y - self.center_y) + self.center_y

    def scale_to(self, scale):
        self.scale_by(scale - self.scale)

    def get_pixel_size(self):
        return self.scale

    def get_size(self):
        return self.scale * Constants.CANVAS_SIZE

    def get_rect(self):
        size = Constants.CANVAS_SIZE / self.scale
        self.rect.width = size
        self.rect.height = size
        return self.rect

    def fit_and_center(self):
        self.scale_to(Constants.DOWNSCALE_BOUND)
        size = self.get_size()
        self.x = self.center_x - size / 2
        self.y = self.center_y - size / 2
