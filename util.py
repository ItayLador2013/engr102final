import pygame
import math
from screeninfo import get_monitors

monitor = get_monitors()[0]


BACKGROUND_COLOR = (135, 206, 235)
SCREEN_WIDTH = monitor.width / 1.5
SCREEN_HEIGHT = monitor.height / 1.5
GRAVITY = 321

PLAYER_FLYING = pygame.image.load("assets/f35-fly.png")
PLAYER_FLYING_WIDTH = 265
PLAYER_FLYING_HEIGHT = 66
ACCELERATION = 400

FLAME = pygame.image.load("assets/f35-flame.png")
FLAME_HEIGHT = 76

MISSILE = pygame.image.load("assets/missile.png")
MISSILE_WIDTH = 192
MISSILE_HEIGHT = 50

BOMB = pygame.image.load("assets/bomb.png")
BOMB_WIDTH = 80
BOMB_HEIGHT = 22

CLOUDS = [
    {"body": pygame.image.load("assets/clouds/1.png"), "width": 1290, "height": 1290},
    {"body": pygame.image.load("assets/clouds/2.png"), "width": 1290, "height": 1290},
    {"body": pygame.image.load("assets/clouds/3.png"), "width": 1292, "height": 1290},
    {"body": pygame.image.load("assets/clouds/4.png"), "width": 1290, "height": 1290},
]

FULL_HEART = pygame.image.load("assets/heart-full.png")
EMPTY_HEART = pygame.image.load("assets/heart-empty.png")
HEART_WIDTH = 41
HEART_HEIGHT = 36
MAX_LIVES = 3
HEARTS_PADDING = 10

DRONE = pygame.image.load("assets/drone1.png")
DRONE_HEIGHT = 28
DRONE_WIDTH = 134
DRONE_SCORE = 10

WARNING = pygame.image.load("assets/warning.png")
WARNING_WIDTH = 50
WARNING_HEIGHT = 45
WARNING_EVERY = 10
WARNING_TIME = 4

ENEMY_MISSILE = pygame.image.load("assets/missile-enemy.png")
ENEMY_MISSILE_WIDTH = 84
ENEMY_MISSILE_HEIGHT = 22

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

EXPLOSIONS = [
    {
        "body": pygame.image.load("assets/explosion1.png"),
        "width": 176,
        "height": 176,
    },
    {
        "body": pygame.image.load("assets/explosion2.png"),
        "width": 276,
        "height": 276,
    },
    {
        "body": pygame.image.load("assets/explosion3.png"),
        "width": 292,
        "height": 196,
    },
    {
        "body": pygame.image.load("assets/explosion4.png"),
        "width": 164,
        "height": 164,
    },
]

SELECTED_COLOR = (0, 200, 83)


def collision(self, obj, plane=False):
    x = self.x if not plane else self.x + self.width * 0.6
    return not (
        x + self.width <= obj.x  # Self is to the left of obj
        or x >= obj.x + obj.width  # Self is to the right of obj
        or self.y + self.height <= obj.y  # Self is above obj
        or self.y >= obj.y + obj.height  # Self is below obj
    )


def radian(degree):
    return (degree * math.pi) / 180
