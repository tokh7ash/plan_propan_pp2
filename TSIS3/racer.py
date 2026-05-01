"""racer.py — core gameplay module for TSIS-3 Racer."""
import pygame
import random
import os
from pygame.locals import *
from ui import (Road, draw_hud, get_font,
                ACCENT, ACCENT2, BLUE_SOFT, RED_SOFT, WHITE, DARK,
                SCREEN_W, SCREEN_H, PANEL, GRAY, BLACK)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ── Colour palette ────────────────────────────────────────────────────────────
CAR_TINTS = {
    "blue":  (60,  140, 255),
    "red":   (255,  60,  60),
    "green": (60,  220,  80),
}

# ── Coin tiers ────────────────────────────────────────────────────────────────
COIN_TIERS = [
    {"tier": "bronze", "value": 1,  "color": (180, 100, 40),  "border": (120, 60, 20),   "weight": 60},
    {"tier": "silver", "value": 3,  "color": (192, 192, 192), "border": (140, 140, 140), "weight": 30},
    {"tier": "gold",   "value": 10, "color": (255, 215, 0),   "border": (180, 140, 0),   "weight": 10},
]

# ── Difficulty presets ────────────────────────────────────────────────────────
DIFFICULTY = {
    "easy":   {"enemy_count": 1, "obstacle_rate": 0.3, "base_speed": 4,  "coins_per_speedup": 15},
    "normal": {"enemy_count": 2, "obstacle_rate": 0.5, "base_speed": 6,  "coins_per_speedup": 10},
    "hard":   {"enemy_count": 3, "obstacle_rate": 0.7, "base_speed": 9,  "coins_per_speedup": 6},
}

# ── Road geometry helpers ─────────────────────────────────────────────────────
ROAD_LEFT  = Road.ROAD_LEFT
ROAD_RIGHT = Road.ROAD_RIGHT
LANE_W     = Road.ROAD_W // Road.LANE_COUNT


def lane_center(lane: int) -> int:
    """Return x-centre of lane 0, 1, or 2."""
    return ROAD_LEFT + LANE_W * lane + LANE_W // 2


# ─────────────────────────────────────────────────────────────────────────────
# Sprite classes
# ─────────────────────────────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self, car_color: str = "blue"):
        super().__init__()
        raw = pygame.image.load(os.path.join(ASSETS_DIR, "player.png")).convert_alpha()
        self.image_orig = pygame.transform.scale(raw, (44, 80))
        # Apply colour tint
        self.image_orig = _tint_surface(self.image_orig, CAR_TINTS.get(car_color, (60, 140, 255)))
        self.image = self.image_orig.copy()
        self.rect  = self.image.get_rect(center=(lane_center(1), 520))

        self.speed      = 5
        self.nitro_on   = False
        self.shield_on  = False
        self.nitro_time = 0.0
        self.shield_hits= 0

    def update(self, dt: float):
        pressed = pygame.key.get_pressed()
        spd = self.speed + (4 if self.nitro_on else 0)

        if self.rect.left > ROAD_LEFT + 2:
            if pressed[K_LEFT]:
                self.rect.move_ip(-spd, 0)
        if self.rect.right < ROAD_RIGHT - 2:
            if pressed[K_RIGHT]:
                self.rect.move_ip(spd, 0)

        # Nitro timer
        if self.nitro_on:
            self.nitro_time -= dt
            if self.nitro_time <= 0:
                self.nitro_on = False

    def apply_powerup(self, kind: str):
        if kind == "nitro":
            self.nitro_on   = True
            self.nitro_time = 4.0
        elif kind == "shield":
            self.shield_on  = True
            self.shield_hits = 1
        elif kind == "repair":
            pass  # handled externally (clear obstacles)

    def active_powerup(self) -> tuple:
        """Return (name, remaining_seconds) or ('', 0)."""
        if self.nitro_on:
            return ("nitro", self.nitro_time)
        if self.shield_on:
            return ("shield", 99.0)
        return ("", 0.0)

    def draw(self, surf: pygame.Surface):
        surf.blit(self.image, self.rect)
        if self.shield_on:
            pygame.draw.circle(surf, (80, 200, 255, 160),
                               self.rect.center, max(self.rect.width, self.rect.height) // 2 + 8, 3)


class Enemy(pygame.sprite.Sprite):
    """Traffic car — moves downward, respawns at top."""

    _SPRITES = ["enemy.png", "car_yellow.png", "car_cyan.png", "car_purple.png"]

    def __init__(self, speed: float = 6):
        super().__init__()
        sprite = random.choice(self._SPRITES)
        try:
            raw = pygame.image.load(os.path.join(ASSETS_DIR, sprite)).convert_alpha()
        except Exception:
            raw = pygame.image.load(os.path.join(ASSETS_DIR, "enemy.png")).convert_alpha()
        self.image = pygame.transform.scale(raw, (44, 80))
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._respawn(safe_y=None)

    def _respawn(self, safe_y):
        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-200, -80))

    def update_speed(self, new_speed: float):
        self.speed = new_speed

    def move(self, player_rect: pygame.Rect):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_H + 10:
            self._respawn(safe_y=player_rect.top)

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        tier = random.choices(COIN_TIERS, weights=[t["weight"] for t in COIN_TIERS], k=1)[0]
        self.value = tier["value"]
        font = get_font(16, bold=True)
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(self.image, tier["color"],  (14, 14), 13)
        pygame.draw.circle(self.image, tier["border"], (14, 14), 13, 2)
        label = font.render("$", True, (60, 40, 0))
        self.image.blit(label, label.get_rect(center=(14, 14)))
        self.rect  = self.image.get_rect()
        self.rect.center = (_rand_road_x(), random.randint(-50, -10))
        self.speed = random.randint(4, 7)

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_H:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Obstacle(pygame.sprite.Sprite):
    """Oil spill, pothole, or speed bump."""
    KINDS = [
        {"name": "oil",    "color": (30, 30, 60),   "size": (50, 22), "effect": "slow"},
        {"name": "pothole","color": (60, 40, 20),   "size": (32, 20), "effect": "slow"},
        {"name": "barrier","color": (255, 160, 0),  "size": (56, 18), "effect": "crash"},
    ]

    def __init__(self):
        super().__init__()
        kind = random.choice(self.KINDS)
        self.effect = kind["effect"]
        self.name   = kind["name"]
        w, h = kind["size"]
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        if kind["name"] == "oil":
            _draw_oil(self.image, w, h)
        elif kind["name"] == "pothole":
            _draw_pothole(self.image, w, h)
        else:
            _draw_barrier(self.image, w, h)
        self.rect  = self.image.get_rect()
        self.rect.center = (_rand_road_x(), random.randint(-120, -20))
        self.speed = random.randint(4, 7)

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_H:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Nitro(pygame.sprite.Sprite):
    """Blue speed strip — nitro boost."""
    def __init__(self):
        super().__init__()
        self.kind  = "nitro"
        self.image = pygame.Surface((44, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (30, 140, 255), (0, 0, 44, 18), border_radius=6)
        label = get_font(12, bold=True).render("NITRO", True, WHITE)
        self.image.blit(label, label.get_rect(center=(22, 9)))
        self.rect  = self.image.get_rect()
        self.rect.center = (_rand_road_x(), -30)
        self.speed = 5
        self.timer = 6.0  # auto-disappear

    def update(self, dt):
        self.rect.move_ip(0, self.speed)
        self.timer -= dt
        if self.rect.top > SCREEN_H or self.timer <= 0:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class PowerUp(pygame.sprite.Sprite):
    ICONS = {
        "shield": ("🛡", (100, 220, 150)),
        "repair": ("🔧", (255, 160, 60)),
    }

    def __init__(self, kind: str):
        super().__init__()
        self.kind  = kind
        icon, col  = self.ICONS.get(kind, ("?", WHITE))
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(self.image, col,   (18, 18), 17)
        pygame.draw.circle(self.image, WHITE, (18, 18), 17, 2)
        label = get_font(18).render(icon, True, DARK)
        self.image.blit(label, label.get_rect(center=(18, 18)))
        self.rect  = self.image.get_rect()
        self.rect.center = (_rand_road_x(), -30)
        self.speed = 4
        self.timer = 7.0

    def update(self, dt):
        self.rect.move_ip(0, self.speed)
        self.timer -= dt
        if self.rect.top > SCREEN_H or self.timer <= 0:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


# ─────────────────────────────────────────────────────────────────────────────
# Main game session
# ─────────────────────────────────────────────────────────────────────────────

class GameSession:
    """Run one full play-through. Returns (score, distance, coins) when done."""

    FINISH_DISTANCE = 2000  # metres to finish line

    def __init__(self, surf: pygame.Surface, clock, settings: dict):
        self.surf     = surf
        self.clock    = clock
        self.settings = settings
        diff_key      = settings.get("difficulty", "normal")
        self.diff     = DIFFICULTY[diff_key]

        # Road
        self.road = Road()
        self.road_speed = self.diff["base_speed"]

        # Player
        car_color   = settings.get("car_color", "blue")
        self.player = Player(car_color)

        # Enemies
        self.enemies = pygame.sprite.Group()
        for _ in range(self.diff["enemy_count"]):
            e = Enemy(speed=self.road_speed + 2)
            self.enemies.add(e)

        # Sprite groups
        self.coins      = pygame.sprite.Group()
        self.obstacles  = pygame.sprite.Group()
        self.powerups   = pygame.sprite.Group()

        # Counters
        self.coins_collected = 0
        self.score           = 0
        self.distance        = 0.0   # metres
        self.last_speedup    = 0
        self.alive           = True
        self.slow_timer      = 0.0   # seconds remaining for oil/pothole slow

        # Timers (ms)
        self.SPAWN_COIN     = USEREVENT + 1
        self.SPAWN_OBSTACLE = USEREVENT + 2
        self.SPAWN_POWERUP  = USEREVENT + 3
        pygame.time.set_timer(self.SPAWN_COIN,     2000)
        pygame.time.set_timer(self.SPAWN_OBSTACLE, 3000)
        pygame.time.set_timer(self.SPAWN_POWERUP,  8000)

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self) -> tuple:
        while True:
            dt = self.clock.tick(60) / 1000.0  # seconds

            result = self._handle_events()
            if result == "quit":
                return (self.score, int(self.distance), self.coins_collected)

            if self.alive:
                self._update(dt)

            self._draw()
            pygame.display.flip()

            if not self.alive:
                pygame.time.set_timer(self.SPAWN_COIN,     0)
                pygame.time.set_timer(self.SPAWN_OBSTACLE, 0)
                pygame.time.set_timer(self.SPAWN_POWERUP,  0)
                return (self.score, int(self.distance), self.coins_collected)

            # Finish line
            if self.distance >= self.FINISH_DISTANCE:
                self.score += 500  # finish bonus
                pygame.time.set_timer(self.SPAWN_COIN,     0)
                pygame.time.set_timer(self.SPAWN_OBSTACLE, 0)
                pygame.time.set_timer(self.SPAWN_POWERUP,  0)
                return (self.score, int(self.distance), self.coins_collected)

    # ── Events ────────────────────────────────────────────────────────────────
    def _handle_events(self) -> str:
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == self.SPAWN_COIN:
                if random.random() < 0.7:
                    self.coins.add(Coin())
            if event.type == self.SPAWN_OBSTACLE:
                if random.random() < self.diff["obstacle_rate"]:
                    # Safe spawn — not directly on player
                    obs = Obstacle()
                    if not obs.rect.colliderect(self.player.rect):
                        self.obstacles.add(obs)
            if event.type == self.SPAWN_POWERUP:
                if random.random() < 0.5:
                    kind = random.choice(["nitro", "shield", "repair"])
                    if kind == "nitro":
                        self.powerups.add(Nitro())
                    else:
                        self.powerups.add(PowerUp(kind))
        return ""

    # ── Update ────────────────────────────────────────────────────────────────
    def _update(self, dt: float):
        # Slow effect
        eff_speed = self.road_speed
        if self.slow_timer > 0:
            self.slow_timer -= dt
            eff_speed = max(1, self.road_speed - 3)

        # Road scroll
        self.road.update(eff_speed)

        # Distance (1 road-speed px ≈ 0.1 m for feel)
        self.distance += eff_speed * dt * 10

        # Player
        self.player.update(dt)

        # Enemies move
        for e in self.enemies:
            e.move(self.player.rect)

        # Coins
        for c in self.coins:
            c.move()

        # Obstacles
        for o in self.obstacles:
            o.move()

        # Power-ups
        for p in self.powerups:
            p.update(dt)

        # ── Collision: enemy ─────────────────────────────────────────────────
        hit = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hit:
            if self.player.shield_on:
                self.player.shield_on  = False
                self.player.shield_hits = 0
                # Push enemy away
                for e in hit:
                    e._respawn(self.player.rect)
            else:
                self.alive = False
                return

        # ── Collision: obstacles ─────────────────────────────────────────────
        obs_hit = pygame.sprite.spritecollide(self.player, self.obstacles, True)
        for o in obs_hit:
            if o.effect == "crash":
                if self.player.shield_on:
                    self.player.shield_on = False
                else:
                    self.alive = False
                    return
            elif o.effect == "slow":
                self.slow_timer = 2.0

        # ── Collision: coins ─────────────────────────────────────────────────
        coin_hit = pygame.sprite.spritecollide(self.player, self.coins, True)
        for c in coin_hit:
            self.coins_collected += c.value
            self.score           += c.value * 10

        # ── Collision: power-ups ─────────────────────────────────────────────
        pu_hit = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pu in pu_hit:
            self.player.apply_powerup(pu.kind)
            if pu.kind == "repair":
                self.obstacles.empty()
                self.slow_timer = 0.0
                self.score += 50

        # ── Difficulty scaling ────────────────────────────────────────────────
        threshold = self.coins_collected // self.diff["coins_per_speedup"]
        if threshold > self.last_speedup:
            steps = threshold - self.last_speedup
            self.road_speed  += steps * 1
            for e in self.enemies:
                e.update_speed(e.speed + steps * 1)
            self.last_speedup = threshold
            # Spawn extra enemy on hard milestones
            if len(self.enemies) < 5 and threshold % 3 == 0:
                self.enemies.add(Enemy(speed=self.road_speed + 2))

        # Score: distance bonus
        self.score = int(self.distance * 0.5 + self.coins_collected * 10)

    # ── Draw ─────────────────────────────────────────────────────────────────
    def _draw(self):
        self.surf.fill((40, 110, 40))  # grass default
        self.road.draw(self.surf)

        # Obstacles, coins, power-ups
        for o in self.obstacles:
            o.draw(self.surf)
        for c in self.coins:
            c.draw(self.surf)
        for p in self.powerups:
            p.draw(self.surf)

        # Enemies
        for e in self.enemies:
            e.draw(self.surf)

        # Player
        self.player.draw(self.surf)

        # HUD
        pu_name, pu_timer = self.player.active_powerup()
        avg_spd = int(sum(e.speed for e in self.enemies) / max(len(self.enemies), 1))
        draw_hud(self.surf,
                 self.coins_collected, self.score,
                 int(self.distance), self.FINISH_DISTANCE,
                 pu_name, pu_timer, avg_spd)

        # Slow effect overlay
        if self.slow_timer > 0:
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            s.fill((80, 50, 0, 60))
            self.surf.blit(s, (0, 0))
            msg = get_font(18, bold=True).render("SLOWED!", True, (255, 200, 50))
            self.surf.blit(msg, msg.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))


# ─────────────────────────────────────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────────────────────────────────────

def _rand_road_x() -> int:
    return random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)


def _tint_surface(surf: pygame.Surface, tint: tuple) -> pygame.Surface:
    tinted = surf.copy()
    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill((*tint, 80))
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


def _draw_oil(surf, w, h):
    pygame.draw.ellipse(surf, (20, 20, 50, 200), (0, 0, w, h))
    # Shine
    pygame.draw.ellipse(surf, (60, 0, 120, 120), (w//4, h//5, w//2, h//3))


def _draw_pothole(surf, w, h):
    pygame.draw.ellipse(surf, (40, 30, 20), (0, 0, w, h))
    pygame.draw.ellipse(surf, (20, 15, 10), (4, 4, w - 8, h - 8))


def _draw_barrier(surf, w, h):
    # Orange/white striped barrier
    stripe_w = 10
    for i in range(w // stripe_w + 1):
        col = (255, 140, 0) if i % 2 == 0 else WHITE
        x   = i * stripe_w
        pygame.draw.rect(surf, col, (x, 0, stripe_w, h))
    pygame.draw.rect(surf, (60, 60, 60), (0, 0, w, h), 2)
