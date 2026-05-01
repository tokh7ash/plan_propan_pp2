"""ui.py — reusable UI helpers for all game screens."""
import pygame
from pygame.locals import *

# ── Colours ──────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK       = (20,  20,  30)
PANEL      = (35,  35,  50)
ACCENT     = (255, 200,  50)   # gold
ACCENT2    = (80,  200, 120)   # green
RED_SOFT   = (220,  80,  80)
BLUE_SOFT  = (80,  140, 220)
GRAY       = (140, 140, 155)
LIGHT_GRAY = (200, 200, 210)

SCREEN_W = 400
SCREEN_H = 600


# ── Font helper ───────────────────────────────────────────────────────────────
_fonts: dict = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("Verdana", size, bold=bold)
    return _fonts[key]


# ── Generic button ────────────────────────────────────────────────────────────
class Button:
    def __init__(self, text: str, rect: pygame.Rect,
                 color=ACCENT, text_color=DARK, font_size: int = 22):
        self.text       = text
        self.rect       = pygame.Rect(rect)
        self.color      = color
        self.hover_col  = tuple(min(255, c + 40) for c in color)
        self.text_color = text_color
        self.font_size  = font_size

    def draw(self, surf: pygame.Surface):
        mx, my = pygame.mouse.get_pos()
        col = self.hover_col if self.rect.collidepoint(mx, my) else self.color
        pygame.draw.rect(surf, col,        self.rect, border_radius=10)
        pygame.draw.rect(surf, WHITE,      self.rect, 2, border_radius=10)
        font = get_font(self.font_size, bold=True)
        label = font.render(self.text, True, self.text_color)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Road background ───────────────────────────────────────────────────────────
class Road:
    """Scrolling road with asphalt, kerbs, centre dashes, and lane lines."""

    ROAD_LEFT  = 60
    ROAD_RIGHT = 340
    ROAD_W     = 280   # ROAD_RIGHT - ROAD_LEFT
    LANE_COUNT = 3
    DASH_H     = 40
    DASH_GAP   = 30

    def __init__(self):
        self.offset = 0.0
        # Pre-compute lane x positions (centres)
        lw = self.ROAD_W / self.LANE_COUNT
        self.lane_centers = [int(self.ROAD_LEFT + lw * i + lw / 2)
                             for i in range(self.LANE_COUNT)]

    def update(self, speed: float):
        self.offset = (self.offset + speed) % (self.DASH_H + self.DASH_GAP)

    def draw(self, surf: pygame.Surface):
        # ── Asphalt ──────────────────────────────────────────────────────────
        pygame.draw.rect(surf, (55, 55, 65),
                         (self.ROAD_LEFT, 0, self.ROAD_W, SCREEN_H))

        # ── Kerb stripes (red/white alternating) — left & right ──────────────
        stripe_h = 20
        num_stripes = SCREEN_H // stripe_h + 2
        for i in range(num_stripes):
            y = int(i * stripe_h - (self.offset % stripe_h))
            col = (220, 50, 50) if i % 2 == 0 else WHITE
            # left kerb
            pygame.draw.rect(surf, col, (self.ROAD_LEFT - 10, y, 10, stripe_h))
            # right kerb
            pygame.draw.rect(surf, col, (self.ROAD_RIGHT,     y, 10, stripe_h))

        # ── Grass ─────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, (40, 110, 40), (0, 0, self.ROAD_LEFT - 10, SCREEN_H))
        pygame.draw.rect(surf, (40, 110, 40),
                         (self.ROAD_RIGHT + 10, 0,
                          SCREEN_W - self.ROAD_RIGHT - 10, SCREEN_H))

        # ── Solid edge lines ──────────────────────────────────────────────────
        pygame.draw.line(surf, WHITE,
                         (self.ROAD_LEFT, 0), (self.ROAD_LEFT, SCREEN_H), 3)
        pygame.draw.line(surf, WHITE,
                         (self.ROAD_RIGHT, 0), (self.ROAD_RIGHT, SCREEN_H), 3)

        # ── Dashed centre lane dividers ───────────────────────────────────────
        lw = self.ROAD_W / self.LANE_COUNT
        for i in range(1, self.LANE_COUNT):
            x = int(self.ROAD_LEFT + lw * i)
            y = int(-self.offset)
            while y < SCREEN_H:
                pygame.draw.rect(surf, (230, 230, 80), (x - 2, y, 4, self.DASH_H))
                y += self.DASH_H + self.DASH_GAP


# ── HUD drawing helpers ───────────────────────────────────────────────────────
def draw_hud(surf: pygame.Surface, coins: int, score: int,
             distance: int, finish: int, powerup_name: str, powerup_timer: float,
             enemy_speed: int):
    """Draw in-game HUD overlay at the top of the screen."""
    # semi-transparent bar
    hud = pygame.Surface((SCREEN_W, 55), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 160))
    surf.blit(hud, (0, 0))

    f  = get_font(17, bold=True)
    fs = get_font(15)

    # Coins
    c_text = f.render(f"Coins: {coins}", True, ACCENT)
    surf.blit(c_text, (8, 6))

    # Score
    s_text = f.render(f"Score: {score}", True, WHITE)
    surf.blit(s_text, (8, 28))

    # Distance
    pct  = min(distance / max(finish, 1), 1.0)
    dist_label = fs.render(f"Dist: {distance}m / {finish}m", True, LIGHT_GRAY)
    surf.blit(dist_label, (SCREEN_W // 2 - dist_label.get_width() // 2, 6))

    # Progress bar
    bar_w = 160
    bar_x = SCREEN_W // 2 - bar_w // 2
    pygame.draw.rect(surf, GRAY,    (bar_x, 30, bar_w, 10), border_radius=4)
    pygame.draw.rect(surf, ACCENT2, (bar_x, 30, int(bar_w * pct), 10), border_radius=4)

    # Power-up indicator
    if powerup_name:
        pu_col = {"nitro": (80, 180, 255), "shield": (100, 255, 150),
                  "repair": (255, 120, 80)}.get(powerup_name, ACCENT)
        pu_text = f.render(f"{powerup_name.upper()} {powerup_timer:.1f}s", True, pu_col)
        surf.blit(pu_text, (SCREEN_W - pu_text.get_width() - 8, 6))

    # Enemy speed
    sp_text = fs.render(f"Spd:{enemy_speed}", True, RED_SOFT)
    surf.blit(sp_text, (SCREEN_W - sp_text.get_width() - 8, 30))


# ── Name entry screen ─────────────────────────────────────────────────────────
def name_entry_screen(surf: pygame.Surface, clock) -> str:
    """Blocking loop — returns the player's entered name."""
    name = ""
    font_big  = get_font(36, bold=True)
    font_med  = get_font(22)
    font_hint = get_font(16)
    cursor_vis = True
    cursor_timer = 0

    while True:
        dt = clock.tick(60)
        cursor_timer += dt
        if cursor_timer > 500:
            cursor_vis  = not cursor_vis
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        surf.fill(DARK)
        title = font_big.render("ENTER YOUR NAME", True, ACCENT)
        surf.blit(title, title.get_rect(center=(SCREEN_W // 2, 180)))

        # Input box
        box = pygame.Rect(80, 260, 240, 50)
        pygame.draw.rect(surf, PANEL, box, border_radius=8)
        pygame.draw.rect(surf, ACCENT, box, 2, border_radius=8)
        display_name = name + ("|" if cursor_vis else " ")
        name_surf = font_med.render(display_name, True, WHITE)
        surf.blit(name_surf, name_surf.get_rect(center=box.center))

        hint = font_hint.render("Press ENTER to continue", True, GRAY)
        surf.blit(hint, hint.get_rect(center=(SCREEN_W // 2, 340)))

        pygame.display.flip()

    return name.strip() or "Player"


# ── Main menu screen ──────────────────────────────────────────────────────────
def main_menu_screen(surf: pygame.Surface, clock) -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    buttons = [
        Button("PLAY",        (125, 220, 150, 48), ACCENT2,    DARK),
        Button("LEADERBOARD", (100, 285, 200, 44), BLUE_SOFT,  WHITE),
        Button("SETTINGS",    (125, 345, 150, 44), PANEL,      WHITE),
        Button("QUIT",        (150, 405, 100, 40), RED_SOFT,   WHITE),
    ]
    actions = ["play", "leaderboard", "settings", "quit"]
    font_title = get_font(42, bold=True)
    font_sub   = get_font(16)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            for btn, act in zip(buttons, actions):
                if btn.is_clicked(event):
                    return act

        surf.fill(DARK)
        # Simple animated road stripes in background
        _draw_menu_bg(surf)

        title = font_title.render("RACER", True, ACCENT)
        surf.blit(title, title.get_rect(center=(SCREEN_W // 2, 120)))
        sub = font_sub.render("TSIS 3  •  Advanced Edition", True, GRAY)
        surf.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 168)))

        for btn in buttons:
            btn.draw(surf)
        pygame.display.flip()


_bg_offset = 0

def _draw_menu_bg(surf: pygame.Surface):
    global _bg_offset
    _bg_offset = (_bg_offset + 2) % 60
    # road strip
    pygame.draw.rect(surf, (50, 50, 60), (120, 0, 160, SCREEN_H))
    for i in range(-1, SCREEN_H // 60 + 2):
        y = i * 60 - _bg_offset
        pygame.draw.rect(surf, (200, 200, 60), (196, y, 8, 35))


# ── Settings screen ───────────────────────────────────────────────────────────
def settings_screen(surf: pygame.Surface, clock, settings: dict) -> dict:
    """Mutates and returns updated settings dict."""
    font_title = get_font(30, bold=True)
    font_lbl   = get_font(20)

    sound_btn  = Button("Sound: ON" if settings["sound"] else "Sound: OFF",
                        (100, 200, 200, 44))
    color_opts = ["blue", "red", "green"]
    diff_opts  = ["easy", "normal", "hard"]
    back_btn   = Button("BACK", (125, 500, 150, 44), RED_SOFT, WHITE)

    def color_btn():
        return Button(f"Car: {settings['car_color'].upper()}",
                      (100, 270, 200, 44), BLUE_SOFT, WHITE)
    def diff_btn():
        return Button(f"Difficulty: {settings['difficulty'].upper()}",
                      (75, 340, 250, 44), PANEL, WHITE)

    cb = color_btn()
    db = diff_btn()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return settings
            if sound_btn.is_clicked(event):
                settings["sound"] = not settings["sound"]
                sound_btn.text = "Sound: ON" if settings["sound"] else "Sound: OFF"
            if cb.is_clicked(event):
                idx = color_opts.index(settings["car_color"])
                settings["car_color"] = color_opts[(idx + 1) % len(color_opts)]
                cb = color_btn()
            if db.is_clicked(event):
                idx = diff_opts.index(settings["difficulty"])
                settings["difficulty"] = diff_opts[(idx + 1) % len(diff_opts)]
                db = diff_btn()
            if back_btn.is_clicked(event):
                return settings

        surf.fill(DARK)
        title = font_title.render("SETTINGS", True, ACCENT)
        surf.blit(title, title.get_rect(center=(SCREEN_W // 2, 130)))

        sound_btn.draw(surf)
        cb.draw(surf)
        db.draw(surf)
        back_btn.draw(surf)

        note = get_font(13).render("Click buttons to cycle options", True, GRAY)
        surf.blit(note, note.get_rect(center=(SCREEN_W // 2, 420)))

        pygame.display.flip()


# ── Leaderboard screen ────────────────────────────────────────────────────────
def leaderboard_screen(surf: pygame.Surface, clock, board: list):
    font_title = get_font(28, bold=True)
    font_row   = get_font(17)
    font_hdr   = get_font(15, bold=True)
    back_btn   = Button("BACK", (125, 540, 150, 44), RED_SOFT, WHITE)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if back_btn.is_clicked(event):
                return

        surf.fill(DARK)
        title = font_title.render("LEADERBOARD", True, ACCENT)
        surf.blit(title, title.get_rect(center=(SCREEN_W // 2, 50)))

        # Header
        hdr = font_hdr.render("#   Name            Score   Dist", True, GRAY)
        surf.blit(hdr, (20, 90))
        pygame.draw.line(surf, GRAY, (20, 110), (380, 110), 1)

        if not board:
            empty = get_font(18).render("No entries yet!", True, GRAY)
            surf.blit(empty, empty.get_rect(center=(SCREEN_W // 2, 300)))
        else:
            for i, entry in enumerate(board[:10]):
                y = 120 + i * 38
                rank_col = [ACCENT, LIGHT_GRAY, (200, 120, 50)] if i < 3 else [WHITE]
                col = rank_col[min(i, len(rank_col) - 1)]
                if i % 2 == 0:
                    pygame.draw.rect(surf, PANEL, (10, y - 4, 380, 34), border_radius=4)
                row = f"{i+1:<3} {entry['name'][:14]:<16} {entry['score']:<8} {entry['distance']}m"
                surf.blit(font_row.render(row, True, col), (18, y))

        back_btn.draw(surf)
        pygame.display.flip()


# ── Game Over screen ──────────────────────────────────────────────────────────
def game_over_screen(surf: pygame.Surface, clock,
                     score: int, distance: int, coins: int) -> str:
    """Returns 'retry' or 'menu'."""
    font_title = get_font(38, bold=True)
    font_stat  = get_font(22)
    retry_btn  = Button("RETRY",  (60,  400, 120, 48), ACCENT2,   DARK)
    menu_btn   = Button("MENU",   (220, 400, 120, 48), BLUE_SOFT,  WHITE)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if retry_btn.is_clicked(event):
                return "retry"
            if menu_btn.is_clicked(event):
                return "menu"

        surf.fill(DARK)
        # Big red flash strip
        pygame.draw.rect(surf, (150, 20, 20), (0, 140, SCREEN_W, 80))
        title = font_title.render("GAME OVER", True, WHITE)
        surf.blit(title, title.get_rect(center=(SCREEN_W // 2, 180)))

        stats = [
            ("Score",    str(score)),
            ("Distance", f"{distance} m"),
            ("Coins",    str(coins)),
        ]
        for i, (label, val) in enumerate(stats):
            y = 285 + i * 36
            l_surf = font_stat.render(label + ":", True, GRAY)
            v_surf = font_stat.render(val,         True, ACCENT)
            surf.blit(l_surf, (80,  y))
            surf.blit(v_surf, (240, y))

        retry_btn.draw(surf)
        menu_btn.draw(surf)
        pygame.display.flip()