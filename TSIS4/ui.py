"""ui.py — reusable UI components and all game screens."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from pygame.locals import *

# ── Colours defined directly here (no circular import risk) ──────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK       = (18,  18,  28)
PANEL      = (35,  35,  55)
GRAY       = (120, 120, 135)
LIGHT_GRAY = (200, 200, 210)
YELLOW     = (255, 215,  50)
GREEN      = (60,  210,  80)
RED        = (213,  50,  80)
ORANGE     = (255, 140,  30)
BLUE       = (50,  140, 220)
CYAN       = (50,  220, 210)
PURPLE     = (160,  60, 220)
ACCENT     = (255, 215,  50)
ACCENT2    = (60,  210,  80)

WIDTH, HEIGHT, HUD_H = 600, 460, 60

# ── Font helper ───────────────────────────────────────────────────────────────
_fonts = {}

def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("Segoe UI", size, bold=bold)
    return _fonts[key]


# ── Button ────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, text, rect, color=None, text_color=None, fsize=22):
        if color is None:
            color = ACCENT
        if text_color is None:
            text_color = DARK
        self.text       = text
        self.rect       = pygame.Rect(rect)
        self.color      = color
        self.hover      = tuple(min(255, c + 40) for c in color)
        self.text_color = text_color
        self.fsize      = fsize

    def draw(self, surf):
        col = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surf, col,   self.rect, border_radius=8)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=8)
        lbl = font(self.fsize, bold=True).render(self.text, True, self.text_color)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Name entry ────────────────────────────────────────────────────────────────
def name_entry_screen(surf, clock):
    name = ""
    cursor_vis, cursor_t = True, 0

    while True:
        dt = clock.tick(60)
        cursor_t += dt
        if cursor_t > 500:
            cursor_vis = not cursor_vis
            cursor_t   = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        surf.fill(DARK)
        _draw_bg_grid(surf)

        title = font(36, True).render("ENTER YOUR NAME", True, ACCENT)
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 160)))

        box = pygame.Rect(150, 230, 300, 50)
        pygame.draw.rect(surf, PANEL, box, border_radius=8)
        pygame.draw.rect(surf, ACCENT, box, 2, border_radius=8)
        display = name + ("|" if cursor_vis else " ")
        n_surf = font(24).render(display, True, WHITE)
        surf.blit(n_surf, n_surf.get_rect(center=box.center))

        hint = font(15).render("Press ENTER to continue", True, GRAY)
        surf.blit(hint, hint.get_rect(center=(WIDTH // 2, 310)))
        pygame.display.flip()


# ── Main menu ─────────────────────────────────────────────────────────────────
def main_menu_screen(surf, clock, personal_best):
    btns = [
        Button("PLAY",        (220, 180, 160, 46), ACCENT2, DARK),
        Button("LEADERBOARD", (195, 242, 210, 44), BLUE,    WHITE),
        Button("SETTINGS",    (220, 302, 160, 44), PANEL,   WHITE),
        Button("QUIT",        (245, 362, 110, 40), RED,     WHITE),
    ]
    acts = ["play", "leaderboard", "settings", "quit"]

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            for btn, act in zip(btns, acts):
                if btn.clicked(event):
                    return act

        surf.fill(DARK)
        _draw_bg_grid(surf)

        t = font(50, True).render("SNAKE", True, ACCENT)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, 100)))
        sub = font(15).render("TSIS-3  |  Advanced Edition", True, GRAY)
        surf.blit(sub, sub.get_rect(center=(WIDTH // 2, 148)))

        if personal_best:
            pb = font(17).render(f"Your best: {personal_best}", True, ACCENT2)
            surf.blit(pb, pb.get_rect(center=(WIDTH // 2, 430)))

        for btn in btns:
            btn.draw(surf)
        pygame.display.flip()


# ── Settings screen ───────────────────────────────────────────────────────────
COLOR_OPTIONS = [
    ("Green",  (60,  210,  80)),
    ("Blue",   (50,  140, 220)),
    ("Cyan",   (50,  220, 210)),
    ("Yellow", (255, 215,  50)),
    ("Red",    (213,  50,  80)),
]

def settings_screen(surf, clock, settings):
    color_idx = 0
    cur = tuple(settings["snake_color"])
    for i, (_, c) in enumerate(COLOR_OPTIONS):
        if tuple(c) == cur:
            color_idx = i
            break

    grid_btn  = Button("Grid: ON"  if settings["grid"]  else "Grid: OFF",  (175, 200, 250, 44))
    sound_btn = Button("Sound: ON" if settings["sound"] else "Sound: OFF", (175, 260, 250, 44))
    save_btn  = Button("SAVE & BACK", (210, 380, 180, 46), ACCENT2, DARK)

    def make_color_btn():
        n, col = COLOR_OPTIONS[color_idx]
        return Button(f"Color: {n}", (175, 320, 250, 44), col,
                      WHITE if sum(col) < 400 else DARK)

    col_btn = make_color_btn()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return settings
            if grid_btn.clicked(event):
                settings["grid"] = not settings["grid"]
                grid_btn.text = "Grid: ON" if settings["grid"] else "Grid: OFF"
            if sound_btn.clicked(event):
                settings["sound"] = not settings["sound"]
                sound_btn.text = "Sound: ON" if settings["sound"] else "Sound: OFF"
            if col_btn.clicked(event):
                color_idx = (color_idx + 1) % len(COLOR_OPTIONS)
                settings["snake_color"] = list(COLOR_OPTIONS[color_idx][1])
                col_btn = make_color_btn()
            if save_btn.clicked(event):
                return settings

        surf.fill(DARK)
        _draw_bg_grid(surf)
        t = font(32, True).render("SETTINGS", True, ACCENT)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, 120)))
        grid_btn.draw(surf)
        sound_btn.draw(surf)
        col_btn.draw(surf)
        save_btn.draw(surf)
        pygame.display.flip()


# ── Leaderboard screen ────────────────────────────────────────────────────────
def leaderboard_screen(surf, clock, board):
    back_btn = Button("BACK", (230, 400, 140, 44), RED, WHITE)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if back_btn.clicked(event):
                return

        surf.fill(DARK)
        _draw_bg_grid(surf)
        t = font(30, True).render("LEADERBOARD", True, ACCENT)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, 45)))

        hdr = font(14, True).render(
            f"{'#':<3} {'Player':<14} {'Score':<8} {'Level':<6} {'Date'}", True, GRAY)
        surf.blit(hdr, (30, 80))
        pygame.draw.line(surf, GRAY, (30, 98), (570, 98), 1)

        if not board:
            msg = font(18).render("No records yet!", True, GRAY)
            surf.blit(msg, msg.get_rect(center=(WIDTH // 2, 240)))
        else:
            for i, e in enumerate(board[:10]):
                y   = 106 + i * 30
                col = [ACCENT, LIGHT_GRAY, (200, 120, 50), WHITE][min(i, 3)]
                if i % 2 == 0:
                    pygame.draw.rect(surf, PANEL, (20, y - 3, 560, 26), border_radius=4)
                row = (f"{i+1:<3} {e['username'][:13]:<14} "
                       f"{e['score']:<8} {e['level']:<6} {e['date']}")
                surf.blit(font(15).render(row, True, col), (28, y))

        back_btn.draw(surf)
        pygame.display.flip()


# ── Game Over screen ──────────────────────────────────────────────────────────
def game_over_screen(surf, clock, score, level, personal_best):
    retry_btn = Button("RETRY",     (130, 330, 140, 46), ACCENT2, DARK)
    menu_btn  = Button("MAIN MENU", (330, 330, 140, 46), BLUE,    WHITE)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if retry_btn.clicked(event):
                return "retry"
            if menu_btn.clicked(event):
                return "menu"

        surf.fill(DARK)
        pygame.draw.rect(surf, (140, 20, 20), (0, 130, WIDTH, 80))
        t = font(40, True).render("GAME OVER", True, WHITE)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, 170)))

        for i, (label, val) in enumerate([
            ("Score",         str(score)),
            ("Level reached", str(level)),
            ("Personal best", str(personal_best)),
        ]):
            y  = 250 + i * 34
            ls = font(20).render(label + ":", True, GRAY)
            vs = font(20, True).render(val,   True, ACCENT)
            surf.blit(ls, (100, y))
            surf.blit(vs, (360, y))

        retry_btn.draw(surf)
        menu_btn.draw(surf)
        pygame.display.flip()


# ── Helper ────────────────────────────────────────────────────────────────────
def _draw_bg_grid(surf):
    for x in range(0, WIDTH, 30):
        pygame.draw.line(surf, (30, 30, 45), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 30):
        pygame.draw.line(surf, (30, 30, 45), (0, y), (WIDTH, y))