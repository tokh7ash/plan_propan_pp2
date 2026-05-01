# config.py — global constants for Snake TSIS-3

WIDTH, HEIGHT = 600, 460   # extra height for HUD bar
HUD_H         = 60         # top bar height
PLAY_H        = HEIGHT - HUD_H  # 400 px play area

BLOCK = 10
FPS   = 60

# Colours
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
DARK        = (18,  18,  28)
PANEL       = (35,  35,  55)
GRAY        = (120, 120, 135)
LIGHT_GRAY  = (200, 200, 210)

YELLOW      = (255, 215,  50)
GREEN       = (60,  210,  80)
GREEN_DIM   = (30,  140,  50)
RED         = (213,  50,  80)
ORANGE      = (255, 140,  30)
BLUE        = (50,  140, 220)
CYAN        = (50,  220, 210)
PURPLE      = (160,  60, 220)
POISON_COL  = (120,   0,  20)
OBSTACLE_COL= (90,   90, 110)

ACCENT      = (255, 215,  50)
ACCENT2     = (60,  210,  80)

# Food types
FOOD_TYPES = [
    {"color": RED,            "value": 1,  "lifetime": 8,  "weight": 6},
    {"color": ORANGE,         "value": 3,  "lifetime": 5,  "weight": 3},
    {"color": YELLOW,         "value": 5,  "lifetime": 3,  "weight": 1},
]

# Power-up definitions
POWERUP_TYPES = [
    {"kind": "speed",  "color": CYAN,              "label": "FAST",   "duration_ms": 5000},
    {"kind": "slow",   "color": PURPLE,             "label": "SLOW",   "duration_ms": 5000},
    {"kind": "shield", "color": (255, 255, 100),    "label": "SHIELD", "duration_ms": 0},
]

POWERUP_FIELD_TTL_MS = 8000

# Difficulty / level
BASE_SPEED            = 15
SPEED_PER_LEVEL       = 3
SCORE_PER_LEVEL       = 5
OBSTACLES_START_LEVEL = 3
OBSTACLES_PER_LEVEL   = 3