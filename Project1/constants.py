import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
LIME = (50, 205, 50)
GOLD = (255, 215, 0)

# Game settings
PLAYER_SPEED = 5
PLAYER_SIZE = (50, 30)
ENEMY_SIZE = (40, 30)
ENEMY_SPEED = 1
ENEMY_DROP_DISTANCE = 40
BULLET_SPEED = 7
POWERUP_FALL_SPEED = 2
POWERUP_SIZE = (30, 30)

# Scoring
ENEMY_POINTS = 100
POWERUP_POINTS = 50

# Powerup types
POWERUP_TYPES = {
    'RAPID_FIRE': {'color': YELLOW, 'duration': 5000, 'symbol': 'R'},
    'TRIPLE_SHOT': {'color': CYAN, 'duration': 5000, 'symbol': '3'},
    'LASER': {'color': RED, 'duration': 4000, 'symbol': 'L'},
    'SPREAD_SHOT': {'color': ORANGE, 'duration': 5000, 'symbol': 'S'},
    'HOMING': {'color': PURPLE, 'duration': 6000, 'symbol': 'H'},
    'PIERCING': {'color': LIME, 'duration': 5000, 'symbol': 'P'},
    'EXPLOSIVE': {'color': RED, 'duration': 4000, 'symbol': 'E'},
    'SHIELD': {'color': BLUE, 'duration': 8000, 'symbol': 'D'},
    'SPEED_BOOST': {'color': GREEN, 'duration': 7000, 'symbol': '+'},
    'SLOW_TIME': {'color': WHITE, 'duration': 4000, 'symbol': 'T'},
    'DOUBLE_POINTS': {'color': GOLD, 'duration': 10000, 'symbol': '2'},
    'MEGA_BOMB': {'color': RED, 'duration': 0, 'symbol': 'B'},
    'FREEZE': {'color': CYAN, 'duration': 3000, 'symbol': 'F'},
    'GHOST': {'color': WHITE, 'duration': 5000, 'symbol': 'G'},
    'CHAIN_LIGHTNING': {'color': YELLOW, 'duration': 4000, 'symbol': 'C'}
}