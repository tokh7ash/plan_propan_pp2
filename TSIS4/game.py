"""game.py — core Snake gameplay session."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import random
import time
from pygame.locals import *
from config import *


# ── Utility ───────────────────────────────────────────────────────────────────

def _snap(v):
    return round(v / BLOCK) * BLOCK

def _rand_cell(exclude_sets, play_top=HUD_H):
    """Random grid cell not in any of the exclude sets."""
    cols = WIDTH  // BLOCK
    rows = PLAY_H // BLOCK
    all_cells = [(c * BLOCK, play_top + r * BLOCK)
                 for c in range(cols) for r in range(rows)]
    excluded = set()
    for s in exclude_sets:
        for item in s:
            excluded.add((int(item[0]), int(item[1])))
    free = [c for c in all_cells if c not in excluded]
    if not free:
        return None
    return random.choice(free)


# ── Food ─────────────────────────────────────────────────────────────────────

def spawn_food(snake_list, obstacles, existing_foods):
    ex = [snake_list, obstacles, existing_foods]
    pos = _rand_cell(ex)
    if pos is None:
        return None
    ft = random.choices(FOOD_TYPES, weights=[f["weight"] for f in FOOD_TYPES])[0]
    return {**ft, "x": pos[0], "y": pos[1], "spawn_time": time.time(), "poison": False}


def spawn_poison(snake_list, obstacles, existing_foods):
    ex = [snake_list, obstacles, existing_foods]
    pos = _rand_cell(ex)
    if pos is None:
        return None
    return {
        "x": pos[0], "y": pos[1],
        "color": POISON_COL, "value": 0,
        "lifetime": 6, "spawn_time": time.time(), "poison": True,
    }


# ── Power-up ──────────────────────────────────────────────────────────────────

def spawn_powerup(snake_list, obstacles, foods):
    ex = [snake_list, obstacles, foods]
    pos = _rand_cell(ex)
    if pos is None:
        return None
    pt = random.choice(POWERUP_TYPES)
    return {**pt, "x": pos[0], "y": pos[1],
            "spawn_ticks": pygame.time.get_ticks()}


# ── Obstacles ─────────────────────────────────────────────────────────────────

def generate_obstacles(snake_head, existing_obs, count):
    """Place `count` new obstacle blocks, not near the snake head."""
    safe_zone = {(snake_head[0] + dx * BLOCK, snake_head[1] + dy * BLOCK)
                 for dx in range(-4, 5) for dy in range(-4, 5)}
    new_obs = set(existing_obs)
    attempts = 0
    while len(new_obs) - len(existing_obs) < count and attempts < 500:
        attempts += 1
        col = random.randint(0, WIDTH  // BLOCK - 1)
        row = random.randint(0, PLAY_H // BLOCK - 1)
        pos = (col * BLOCK, HUD_H + row * BLOCK)
        if pos not in safe_zone and pos not in new_obs:
            new_obs.add(pos)
    return new_obs


# ── HUD drawing ───────────────────────────────────────────────────────────────

def draw_hud(surf, score, level, personal_best, active_pu, pu_end_ticks, shield_on):
    pygame.draw.rect(surf, (20, 20, 35), (0, 0, WIDTH, HUD_H))
    pygame.draw.line(surf, GRAY, (0, HUD_H), (WIDTH, HUD_H), 1)

    f  = pygame.font.SysFont("Segoe UI", 20, bold=True)
    fs = pygame.font.SysFont("Segoe UI", 16)

    surf.blit(f.render(f"Score: {score}", True, YELLOW),  (10, 10))
    surf.blit(f.render(f"Level: {level}", True, WHITE),   (10, 33))

    if personal_best:
        pb = fs.render(f"Best: {personal_best}", True, GRAY)
        surf.blit(pb, (WIDTH // 2 - pb.get_width() // 2, 22))

    # Power-up indicator
    if shield_on:
        pu_surf = f.render("SHIELD ACTIVE", True, (255,255,100))
        surf.blit(pu_surf, (WIDTH - pu_surf.get_width() - 10, 10))
    elif active_pu:
        now   = pygame.time.get_ticks()
        rem_s = max(0, (pu_end_ticks - now) / 1000)
        col   = CYAN if active_pu == "speed" else PURPLE
        pu_surf = f.render(f"{active_pu.upper()} {rem_s:.1f}s", True, col)
        surf.blit(pu_surf, (WIDTH - pu_surf.get_width() - 10, 10))


# ── Grid overlay ──────────────────────────────────────────────────────────────

def draw_grid(surf):
    for x in range(0, WIDTH, BLOCK):
        pygame.draw.line(surf, (30, 32, 40), (x, HUD_H), (x, HEIGHT))
    for y in range(HUD_H, HEIGHT, BLOCK):
        pygame.draw.line(surf, (30, 32, 40), (0, y), (WIDTH, y))


# ── Main game session ─────────────────────────────────────────────────────────

class GameSession:
    """One full play-through. Returns (score, level) when done."""

    FOOD_SPAWN_INTERVAL = 5000   # ms between extra food spawns
    POISON_INTERVAL     = 12000  # ms between poison spawns
    PU_INTERVAL         = 15000  # ms between power-up spawns

    def __init__(self, surf, clock, settings: dict, personal_best: int):
        self.surf          = surf
        self.clock         = clock
        self.settings      = settings
        self.personal_best = personal_best

        self.snake_color = tuple(settings["snake_color"])

        # Snake state
        self.x = _snap(WIDTH  / 2)
        self.y = _snap(HUD_H + PLAY_H / 2)
        self.dx, self.dy = BLOCK, 0
        self.body  = [[self.x, self.y]]
        self.length = 1

        # Game state
        self.score  = 0
        self.level  = 1
        self.speed  = BASE_SPEED
        self.alive  = True

        # Power-up state
        self.active_pu   = None   # "speed" | "slow" | None
        self.pu_end      = 0
        self.shield_on   = False
        self.shield_used = False

        # Obstacles
        self.obstacles: set = set()

        # Food / poison / power-up on field
        self.foods: list   = []
        self.poison        = None
        self.field_pu      = None   # power-up item on the field

        # Spawn first food
        f = spawn_food(self.body, self.obstacles, [])
        if f: self.foods.append(f)

        # Timers (ms ticks)
        self.last_food_spawn   = pygame.time.get_ticks()
        self.last_poison_spawn = pygame.time.get_ticks()
        self.last_pu_spawn     = pygame.time.get_ticks()

    # ── run ───────────────────────────────────────────────────────────────────
    def run(self) -> tuple:
        while self.alive:
            self._handle_events()
            if not self.alive:
                break
            self._update()
            self._draw()
            self.clock.tick(self._current_speed())

        return (self.score, self.level)

    # ── events ────────────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.alive = False
                return
            if event.type == KEYDOWN:
                if event.key == K_LEFT  and self.dx == 0:
                    self.dx, self.dy = -BLOCK, 0
                elif event.key == K_RIGHT and self.dx == 0:
                    self.dx, self.dy =  BLOCK, 0
                elif event.key == K_UP    and self.dy == 0:
                    self.dx, self.dy = 0, -BLOCK
                elif event.key == K_DOWN  and self.dy == 0:
                    self.dx, self.dy = 0,  BLOCK

    # ── update ────────────────────────────────────────────────────────────────
    def _update(self):
        now = pygame.time.get_ticks()

        # Move snake
        self.x += self.dx
        self.y += self.dy
        head = [self.x, self.y]

        # Wall collision
        if (self.x < 0 or self.x >= WIDTH or
                self.y < HUD_H or self.y >= HEIGHT):
            if self.shield_on:
                self._use_shield()
                # Wrap around
                self.x = max(0, min(WIDTH  - BLOCK, self.x))
                self.y = max(HUD_H, min(HEIGHT - BLOCK, self.y))
                head   = [self.x, self.y]
            else:
                self.alive = False; return

        # Obstacle collision
        if (self.x, self.y) in self.obstacles:
            if self.shield_on:
                self._use_shield()
            else:
                self.alive = False; return

        # Self collision
        self.body.append(head)
        if len(self.body) > self.length:
            del self.body[0]

        for seg in self.body[:-1]:
            if seg == head:
                if self.shield_on:
                    self._use_shield()
                else:
                    self.alive = False; return

        # Expire active power-up
        if self.active_pu and now > self.pu_end:
            self.active_pu = None

        # ── Spawn timers ──────────────────────────────────────────────────────
        if now - self.last_food_spawn > self.FOOD_SPAWN_INTERVAL:
            self.last_food_spawn = now
            if len(self.foods) < 3:
                f = spawn_food(self.body, self.obstacles,
                               [(fd["x"], fd["y"]) for fd in self.foods])
                if f: self.foods.append(f)

        if now - self.last_poison_spawn > self.POISON_INTERVAL:
            self.last_poison_spawn = now
            if self.poison is None:
                ex = [(fd["x"], fd["y"]) for fd in self.foods]
                self.poison = spawn_poison(self.body, self.obstacles, ex)

        if now - self.last_pu_spawn > self.PU_INTERVAL:
            self.last_pu_spawn = now
            if self.field_pu is None:
                ex = ([(fd["x"], fd["y"]) for fd in self.foods] +
                      ([(self.poison["x"], self.poison["y"])] if self.poison else []))
                self.field_pu = spawn_powerup(self.body, self.obstacles, ex)

        # ── Expire field items ────────────────────────────────────────────────
        t_now = time.time()
        self.foods = [fd for fd in self.foods
                      if t_now - fd["spawn_time"] < fd["lifetime"]]
        if self.poison and t_now - self.poison["spawn_time"] >= self.poison["lifetime"]:
            self.poison = None
        if self.field_pu:
            age = pygame.time.get_ticks() - self.field_pu["spawn_ticks"]
            if age > POWERUP_FIELD_TTL_MS:
                self.field_pu = None

        # ── Eat food ─────────────────────────────────────────────────────────
        eaten = [fd for fd in self.foods if fd["x"] == self.x and fd["y"] == self.y]
        for fd in eaten:
            self.foods.remove(fd)
            self.length  += 1
            self.score   += fd["value"]
            self._check_level_up()

        # Eat poison
        if self.poison and self.poison["x"] == self.x and self.poison["y"] == self.y:
            self.poison = None
            self.length = max(1, self.length - 2)
            if self.length <= 1 and len(self.body) <= 1:
                self.alive = False; return
            # Trim body if too long
            while len(self.body) > self.length:
                del self.body[0]

        # Eat power-up
        if (self.field_pu and
                self.field_pu["x"] == self.x and self.field_pu["y"] == self.y):
            self._activate_powerup(self.field_pu)
            self.field_pu = None

    # ── draw ─────────────────────────────────────────────────────────────────
    def _draw(self):
        self.surf.fill(DARK)
        if self.settings.get("grid"):
            draw_grid(self.surf)

        # Obstacles
        for ox, oy in self.obstacles:
            pygame.draw.rect(self.surf, OBSTACLE_COL, (ox, oy, BLOCK, BLOCK))
            pygame.draw.rect(self.surf, (60,60,75),   (ox, oy, BLOCK, BLOCK), 1)

        # Foods
        fs = pygame.font.SysFont("Segoe UI", 13)
        for fd in self.foods:
            pygame.draw.rect(self.surf, fd["color"], (fd["x"], fd["y"], BLOCK, BLOCK))
            rem = fd["lifetime"] - (time.time() - fd["spawn_time"])
            col = RED if rem < 2 else WHITE
            t = fs.render(f"{rem:.0f}", True, col)
            self.surf.blit(t, (fd["x"] - 2, fd["y"] - 14))

        # Poison
        if self.poison:
            px, py = self.poison["x"], self.poison["y"]
            pygame.draw.rect(self.surf, POISON_COL, (px, py, BLOCK, BLOCK))
            pygame.draw.rect(self.surf, (200, 0, 40), (px, py, BLOCK, BLOCK), 1)
            pt = fs.render("P", True, (255, 80, 80))
            self.surf.blit(pt, (px, py - 13))

        # Field power-up
        if self.field_pu:
            fx, fy = self.field_pu["x"], self.field_pu["y"]
            pygame.draw.rect(self.surf, self.field_pu["color"], (fx, fy, BLOCK, BLOCK))
            age   = pygame.time.get_ticks() - self.field_pu["spawn_ticks"]
            rem   = (POWERUP_FIELD_TTL_MS - age) / 1000
            lt    = fs.render(self.field_pu["label"], True, DARK)
            self.surf.blit(lt, (fx - lt.get_width()//2 + 5, fy - 14))

        # Snake
        for i, seg in enumerate(self.body):
            col = self.snake_color if i < len(self.body)-1 else WHITE
            pygame.draw.rect(self.surf, col, (seg[0], seg[1], BLOCK, BLOCK))
            pygame.draw.rect(self.surf, DARK,(seg[0], seg[1], BLOCK, BLOCK), 1)

        # Shield flash on head
        if self.shield_on:
            hx, hy = self.body[-1]
            pygame.draw.rect(self.surf, (255,255,100), (hx-2, hy-2, BLOCK+4, BLOCK+4), 2)

        draw_hud(self.surf, self.score, self.level, self.personal_best,
                 self.active_pu, self.pu_end, self.shield_on)
        pygame.display.flip()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _current_speed(self) -> int:
        if self.active_pu == "speed": return self.speed + 8
        if self.active_pu == "slow":  return max(5, self.speed - 6)
        return self.speed

    def _check_level_up(self):
        new_level = self.score // SCORE_PER_LEVEL + 1
        if new_level > self.level:
            self.level = new_level
            self.speed = BASE_SPEED + (self.level - 1) * SPEED_PER_LEVEL
            if self.level >= OBSTACLES_START_LEVEL:
                self.obstacles = generate_obstacles(
                    self.body[-1], self.obstacles, OBSTACLES_PER_LEVEL)

    def _activate_powerup(self, pu: dict):
        if pu["kind"] == "shield":
            self.shield_on = True
        else:
            self.active_pu = pu["kind"]
            self.pu_end    = pygame.time.get_ticks() + pu["duration_ms"]

    def _use_shield(self):
        self.shield_on   = False
        self.shield_used = True