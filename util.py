import pygame #import pygame which is a library for graphics
import math
import random 

BACKGROUND_COLOR = (135, 206, 235) #the sky color
SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720
GRAVITY = 321 #accaliration due to gravity

PLAYER_FLYING = pygame.image.load("assets/f35-fly.png") #load the player jet image
PLAYER_FLYING_WIDTH = 265
PLAYER_FLYING_HEIGHT = 66
ACCELERATION = 400 #acceleration constant for player missiles

MISSILE = pygame.image.load("assets/missile.png") #load the missile image
MISSILE_WIDTH = 192
MISSILE_HEIGHT = 50 

#load the different clouds their images and their respective dimensions
CLOUDS = [
    {
        "body": pygame.image.load("assets/clouds/1.png"),
        "width": 1290,
        "height": 1290
    },
    {
        "body": pygame.image.load("assets/clouds/2.png"),
        "width": 1290,
        "height": 1290
    },
    {
        "body": pygame.image.load("assets/clouds/3.png"),
        "width": 1292,
        "height": 1290
    },
    {
        "body": pygame.image.load("assets/clouds/4.png"),
        "width": 1290,
        "height": 1290
    },
]

#load the hear images
FULL_HEART = pygame.image.load("assets/heart-full.png")
EMPTY_HEART = pygame.image.load("assets/heart-empty.png")
HEART_WIDTH = 41
HEART_HEIGHT = 36

MAX_LIVES = 3 #max number of lives
HEARTS_PADDING = 10 #padding for the heart graphics

DRONE = pygame.image.load("assets/drone1.png") #load enemy drone image
DRONE_HEIGHT = 28
DRONE_WIDTH = 134
DRONE_SCORE = 10 #score increase for every drone destroyed

WARNING = pygame.image.load("assets/warning.png") #load the warning image
WARNING_WIDTH = 50
WARNING_HEIGHT = 45

WARNING_EVERY = 10 #constant for warning every period of time
WARNING_TIME = 4 #constant for how much time the warning exists before enemy missile coming


ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" #the alphabet - loaded like this for working with indecies

#load the different explosions their images and their respective dimensions
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

SELECTED_COLOR = (0, 200, 83) #the color of selected text

def collision(self, obj, plane=False) -> bool:
    """finds wheter object's rectangle dimensions overlap - returns True if yes and False if no"""
    x = self.x if not plane else self.x + self.width * 0.6 
    return not (
        x + self.width <= obj.x or  #self is to the left of obj
        x >= obj.x + obj.width or   #self is to the right of obj
        self.y + self.height <= obj.y or #self is above obj
        self.y >= obj.y + obj.height     #self is below obj
    )

def radian(degree) -> float:
    """convert degrees to radians"""
    return (degree * math.pi) / 180

