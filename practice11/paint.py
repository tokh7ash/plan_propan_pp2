import pygame
import sys
import math

# Константы окна
TOOLBAR_H = 90       # высота панели (два ряда)
CANVAS_W  = 640
CANVAS_H  = 480
WIN_W     = CANVAS_W
WIN_H     = CANVAS_H + TOOLBAR_H

# Цвета интерфейса
BG_TOOLBAR = (28, 28, 38)
BORDER_COL = (60, 60, 80)
CANVAS_BG  = (0, 0, 0)
WHITE      = (255, 255, 255)
GRAY       = (160, 160, 160)
BTN_ACTIVE = (70, 130, 200)
BTN_NORMAL = (50, 50, 65)

# Цвета палитры
PALETTE = [
    (0,   0,   255),
    (255, 0,   0  ),
    (0,   255, 0  ),
    (255, 255, 0  ),
    (255, 165, 0  ),
    (255, 255, 255),
]

# Все инструменты в тулбаре (ряд 1 и ряд 2)
ROW1_TOOLS = [
    ('draw',      'Кисть'),
    ('erase',     'Ластик'),
    ('rect',      'Прямоугольник'),
    ('square',    'Квадрат'),
]
ROW2_TOOLS = [
    ('rtriangle', 'П треугольник'),
    ('etriangle', 'Р треугольник'),
    ('rhombus',   'Ромб'),
    ('circle',    'Круг'),           # НОВОЕ
]

# Все инструменты вместе
ALL_TOOLS = ROW1_TOOLS + ROW2_TOOLS

SHAPE_TOOLS = {'rect', 'square', 'rtriangle', 'etriangle', 'rhombus', 'circle'}  # НОВОЕ: circle


def get_triangle_points(p1, p2, kind):
    """Три вершины треугольника по двум точкам.
    kind='right' — прямоугольный, kind='equil' — равносторонний."""
    if kind == 'right':
        return [p1, (p2[0], p1[1]), p2]
    else:
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        apex = (int(mx - dy * math.sqrt(3) / 2), int(my + dx * math.sqrt(3) / 2))
        return [p1, p2, apex]


def get_rhombus_points(p1, p2):
    """4 вершины ромба по двум углам выделения."""
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    dx = abs(p2[0] - p1[0]) // 2
    dy = abs(p2[1] - p1[1]) // 2
    return [(cx, cy - dy), (cx + dx, cy), (cx, cy + dy), (cx - dx, cy)]


def get_square_rect(p1, p2):
    """(x, y, side, side) квадрата — сторона = min(w, h)."""
    side = min(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
    sx = p1[0] if p2[0] >= p1[0] else p1[0] - side
    sy = p1[1] if p2[1] >= p1[1] else p1[1] - side
    return (sx, sy, side, side)


def build_buttons(font):
    """Создаёт прямоугольники кнопок инструментов (два ряда) и палитры."""
    buttons = []

    # Ряд 1 — 4 кнопки
    bw1 = WIN_W // len(ROW1_TOOLS)
    for i, (tid, label) in enumerate(ROW1_TOOLS):
        rect = pygame.Rect(i * bw1, 1, bw1 - 2, 40)
        buttons.append((rect, tid, label))

    # Ряд 2 — 4 кнопки + палитра справа от них
    bw2 = (WIN_W // 2) // len(ROW2_TOOLS)
    for i, (tid, label) in enumerate(ROW2_TOOLS):
        rect = pygame.Rect(i * bw2, 46, bw2 - 2, 40)
        buttons.append((rect, tid, label))

    # Палитра — цветные кружки справа в ряду 2
    palette_rects = []
    start_x = (WIN_W // 2) + 10
    for i, color in enumerate(PALETTE):
        cx = start_x + i * 34
        rect = pygame.Rect(cx - 13, 53, 26, 26)
        palette_rects.append((rect, color))

    return buttons, palette_rects


def draw_toolbar(screen, font, buttons, palette_rects, cur_mode, cur_color, radius):
    """Рисует тулбар: два ряда кнопок + палитра + размер кисти."""
    pygame.draw.rect(screen, BG_TOOLBAR, (0, 0, WIN_W, TOOLBAR_H))
    pygame.draw.line(screen, BORDER_COL, (0, TOOLBAR_H - 1), (WIN_W, TOOLBAR_H - 1), 1)
    pygame.draw.line(screen, BORDER_COL, (0, 43), (WIN_W, 43), 1)

    # Кнопки инструментов
    for rect, tid, label in buttons:
        col = BTN_ACTIVE if tid == cur_mode else BTN_NORMAL
        pygame.draw.rect(screen, col, rect, border_radius=5)
        txt = font.render(label, True, WHITE)
        screen.blit(txt, (rect.x + (rect.w - txt.get_width()) // 2,
                          rect.y + (rect.h - txt.get_height()) // 2))

    # Цветовые кружки палитры
    for rect, color in palette_rects:
        pygame.draw.circle(screen, color, rect.center, 13)
        if color == cur_color:
            pygame.draw.circle(screen, WHITE, rect.center, 15, 2)

    # Размер кисти (правый край)
    size_txt = font.render(f"Размер: {radius}", True, GRAY)
    screen.blit(size_txt, (WIN_W - size_txt.get_width() - 10, 57))


def draw_shape_preview(screen, cur_mode, p1, p2):
    """Серое превью фигуры пока зажата мышь."""
    col = (180, 180, 180)

    if cur_mode == 'rect':
        x = min(p1[0], p2[0])
        y = min(p1[1], p2[1]) + TOOLBAR_H
        pygame.draw.rect(screen, col, (x, y, abs(p2[0]-p1[0]), abs(p2[1]-p1[1])), 1)

    elif cur_mode == 'square':
        rx, ry, rw, rh = get_square_rect(p1, p2)
        pygame.draw.rect(screen, col, (rx, ry + TOOLBAR_H, rw, rh), 1)

    elif cur_mode == 'rtriangle':
        pts = [(px, py + TOOLBAR_H) for px, py in get_triangle_points(p1, p2, 'right')]
        pygame.draw.polygon(screen, col, pts, 1)

    elif cur_mode == 'etriangle':
        pts = [(px, py + TOOLBAR_H) for px, py in get_triangle_points(p1, p2, 'equil')]
        pygame.draw.polygon(screen, col, pts, 1)

    elif cur_mode == 'rhombus':
        pts = [(px, py + TOOLBAR_H) for px, py in get_rhombus_points(p1, p2)]
        pygame.draw.polygon(screen, col, pts, 1)

    # НОВОЕ: превью круга
    elif cur_mode == 'circle':
        cx, cy = p1
        r = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]))
        pygame.draw.circle(screen, col, (cx, cy + TOOLBAR_H), r, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 13)

    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    # Строим кнопки и палитру один раз
    buttons, palette_rects = build_buttons(font)

    # Состояние
    radius      = 5
    drawing     = False
    last_pos    = None
    cur_color   = PALETTE[0]
    cur_mode    = 'draw'
    shape_start = None   # начальная точка при рисовании фигуры

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:        canvas.fill(CANVAS_BG)
                elif event.key == pygame.K_ESCAPE: return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Колесо мыши — размер кисти
                if event.button == 4: radius = min(50, radius + 1)
                if event.button == 5: radius = max(1,  radius - 1)

                # Клик в тулбар
                if my < TOOLBAR_H:
                    for rect, tid, label in buttons:
                        if rect.collidepoint(mx, my):
                            cur_mode = tid
                    for rect, color in palette_rects:
                        if rect.collidepoint(mx, my):
                            cur_color = color
                    continue  # не рисуем на холсте

                # Клик на холсте
                canvas_y = my - TOOLBAR_H
                if event.button == 1:
                    if cur_mode in SHAPE_TOOLS:
                        shape_start = (mx, canvas_y)
                    else:
                        drawing = True

            if event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                canvas_y = my - TOOLBAR_H

                if event.button == 1:
                    if shape_start and cur_mode in SHAPE_TOOLS:
                        p1 = shape_start
                        p2 = (mx, canvas_y)

                        # Рисуем финальную фигуру на холсте
                        if cur_mode == 'rect':
                            x = min(p1[0], p2[0])
                            y = min(p1[1], p2[1])
                            pygame.draw.rect(canvas, cur_color,
                                             (x, y, abs(p2[0]-p1[0]), abs(p2[1]-p1[1])), 2)

                        elif cur_mode == 'square':
                            pygame.draw.rect(canvas, cur_color, get_square_rect(p1, p2), 2)

                        elif cur_mode == 'rtriangle':
                            pygame.draw.polygon(canvas, cur_color,
                                                get_triangle_points(p1, p2, 'right'), 2)

                        elif cur_mode == 'etriangle':
                            pygame.draw.polygon(canvas, cur_color,
                                                get_triangle_points(p1, p2, 'equil'), 2)

                        elif cur_mode == 'rhombus':
                            pygame.draw.polygon(canvas, cur_color,
                                                get_rhombus_points(p1, p2), 2)

                        # НОВОЕ: финальный круг
                        elif cur_mode == 'circle':
                            r = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]))
                            pygame.draw.circle(canvas, cur_color, p1, r, 2)

                        shape_start = None
                    else:
                        drawing  = False
                        last_pos = None

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                canvas_y = my - TOOLBAR_H

                if drawing and canvas_y >= 0:
                    cur_pos = (mx, canvas_y)
                    color = CANVAS_BG if cur_mode == 'erase' else cur_color

                    if last_pos:
                        pygame.draw.line(canvas, color, last_pos, cur_pos, radius * 2)
                        pygame.draw.circle(canvas, color, cur_pos, radius)
                    else:
                        pygame.draw.circle(canvas, color, cur_pos, radius)

                    last_pos = cur_pos

        # ── Отрисовка кадра ─────────────────────
        screen.fill((30, 30, 30))
        screen.blit(canvas, (0, TOOLBAR_H))

        # Превью фигуры пока зажата мышь
        if shape_start and pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            draw_shape_preview(screen, cur_mode, shape_start, (mx, my - TOOLBAR_H))

        # Курсор-кружок
        indicator = WHITE if cur_mode == 'erase' else cur_color
        pygame.draw.circle(screen, indicator, pygame.mouse.get_pos(), radius, 1)

        draw_toolbar(screen, font, buttons, palette_rects, cur_mode, cur_color, radius)

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()