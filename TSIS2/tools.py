import pygame
import math
from collections import deque

# ─── Константы толщин ────────────────────────────────────────────────────────
SIZES = {1: 5, 2: 10, 3: 40}   # клавиша → пиксели


# ─── Вспомогательные геометрические функции ──────────────────────────────────

def get_triangle_points(p1, p2, kind):
    if kind == 'right':
        return [p1, (p2[0], p1[1]), p2]
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    apex = (int(mx - dy * math.sqrt(3) / 2),
            int(my + dx * math.sqrt(3) / 2))
    return [p1, p2, apex]


def get_rhombus_points(p1, p2):
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    dx = abs(p2[0] - p1[0]) // 2
    dy = abs(p2[1] - p1[1]) // 2
    return [(cx, cy - dy), (cx + dx, cy), (cx, cy + dy), (cx - dx, cy)]


def get_square_rect(p1, p2):
    side = min(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
    sx = p1[0] if p2[0] >= p1[0] else p1[0] - side
    sy = p1[1] if p2[1] >= p1[1] else p1[1] - side
    return (sx, sy, side, side)


# ─── Flood-fill ───────────────────────────────────────────────────────────────

def flood_fill(surface, pos, fill_color):
    """BFS flood-fill по точному совпадению цвета."""
    x0, y0 = pos
    w, h = surface.get_size()
    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target = surface.get_at((x0, y0))[:3]
    fc = fill_color[:3]
    if target == fc:
        return

    visited = set()
    queue = deque()
    queue.append((x0, y0))
    visited.add((x0, y0))

    surface.lock()
    while queue:
        cx, cy = queue.popleft()
        surface.set_at((cx, cy), fill_color)
        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if (0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in visited
                    and surface.get_at((nx, ny))[:3] == target):
                visited.add((nx, ny))
                queue.append((nx, ny))
    surface.unlock()


# ─── Финальная отрисовка фигуры на холсте ────────────────────────────────────

def draw_shape_final(canvas, mode, p1, p2, color, thickness):
    if mode == 'rect':
        x = min(p1[0], p2[0]);  y = min(p1[1], p2[1])
        pygame.draw.rect(canvas, color,
                         (x, y, abs(p2[0]-p1[0]), abs(p2[1]-p1[1])), thickness)

    elif mode == 'square':
        pygame.draw.rect(canvas, color, get_square_rect(p1, p2), thickness)

    elif mode == 'rtriangle':
        pygame.draw.polygon(canvas, color,
                            get_triangle_points(p1, p2, 'right'), thickness)

    elif mode == 'etriangle':
        pygame.draw.polygon(canvas, color,
                            get_triangle_points(p1, p2, 'equil'), thickness)

    elif mode == 'rhombus':
        pygame.draw.polygon(canvas, color,
                            get_rhombus_points(p1, p2), thickness)

    elif mode == 'circle':
        r = int(math.hypot(p2[0]-p1[0], p2[1]-p1[1]))
        if r > 0:
            pygame.draw.circle(canvas, color, p1, r, thickness)

    elif mode == 'line':
        pygame.draw.line(canvas, color, p1, p2, thickness)


# ─── Превью фигуры пока зажата мышь ──────────────────────────────────────────

def draw_shape_preview(screen, mode, p1, p2, toolbar_h, thickness):
    col = (180, 180, 180)
    th = max(1, thickness)

    def shift(pts):
        return [(px, py + toolbar_h) for px, py in pts]

    if mode == 'rect':
        x = min(p1[0], p2[0]);  y = min(p1[1], p2[1]) + toolbar_h
        pygame.draw.rect(screen, col,
                         (x, y, abs(p2[0]-p1[0]), abs(p2[1]-p1[1])), th)

    elif mode == 'square':
        rx, ry, rw, rh = get_square_rect(p1, p2)
        pygame.draw.rect(screen, col, (rx, ry + toolbar_h, rw, rh), th)

    elif mode == 'rtriangle':
        pygame.draw.polygon(screen, col,
                            shift(get_triangle_points(p1, p2, 'right')), th)

    elif mode == 'etriangle':
        pygame.draw.polygon(screen, col,
                            shift(get_triangle_points(p1, p2, 'equil')), th)

    elif mode == 'rhombus':
        pygame.draw.polygon(screen, col,
                            shift(get_rhombus_points(p1, p2)), th)

    elif mode == 'circle':
        r = int(math.hypot(p2[0]-p1[0], p2[1]-p1[1]))
        if r > 0:
            pygame.draw.circle(screen, col,
                               (p1[0], p1[1] + toolbar_h), r, th)

    elif mode == 'line':
        pygame.draw.line(screen, col,
                         (p1[0], p1[1] + toolbar_h),
                         (p2[0], p2[1] + toolbar_h), th)
