"""
Paint — расширенная версия (Practice 12)
Новые возможности:
  • Карандаш (freehand)               — непрерывная линия
  • Прямая линия с превью             — line tool
  • Три размера кисти (1/2/3 на клав.)
  • Flood-fill                        — заливка замкнутой области
  • Сохранение Ctrl+S                 → PNG с меткой времени
  • Текстовый инструмент              — клик → ввод → Enter фиксирует
"""

import pygame
import sys
import math
import datetime

from tools import (
    SIZES, flood_fill,
    draw_shape_final, draw_shape_preview,
)

# ─── Константы ────────────────────────────────────────────────────────────────
TOOLBAR_H = 100
CANVAS_W  = 800
CANVAS_H  = 550
WIN_W     = CANVAS_W
WIN_H     = CANVAS_H + TOOLBAR_H

# Интерфейсные цвета
BG_TOOLBAR = (22, 22, 32)
BORDER_COL = (55, 55, 75)
CANVAS_BG  = (255, 255, 255)
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GRAY       = (150, 150, 150)
BTN_ACTIVE = (60, 130, 210)
BTN_HOVER  = (75, 75, 100)
BTN_NORMAL = (42, 42, 58)

# Палитра
PALETTE = [
    (0,   0,   0  ),
    (255, 255, 255),
    (220, 50,  50 ),
    (50,  130, 220),
    (50,  200, 80 ),
    (240, 210, 40 ),
    (240, 130, 30 ),
    (160, 60,  200),
    (0,   200, 200),
    (180, 100, 60 ),
]

# ─── Описание инструментов ────────────────────────────────────────────────────
ROW1_TOOLS = [
    ('pencil',    'Карандаш'),
    ('line',      'Линия'),
    ('erase',     'Ластик'),
    ('fill',      'Заливка'),
    ('text',      'Текст'),
]
ROW2_TOOLS = [
    ('rect',      'Прямоуг.'),
    ('square',    'Квадрат'),
    ('circle',    'Круг'),
    ('rtriangle', 'П.треуг.'),
    ('etriangle', 'Р.треуг.'),
    ('rhombus',   'Ромб'),
]
ALL_TOOLS = ROW1_TOOLS + ROW2_TOOLS

# Инструменты, использующие drag-to-shape
SHAPE_TOOLS = {'rect', 'square', 'circle', 'rtriangle', 'etriangle', 'rhombus', 'line'}


# ─── Построение кнопок ────────────────────────────────────────────────────────

def build_buttons():
    buttons = []
    bw1 = WIN_W // len(ROW1_TOOLS)
    for i, (tid, label) in enumerate(ROW1_TOOLS):
        rect = pygame.Rect(i * bw1, 1, bw1 - 2, 38)
        buttons.append((rect, tid, label))

    bw2 = (WIN_W * 3 // 5) // len(ROW2_TOOLS)
    for i, (tid, label) in enumerate(ROW2_TOOLS):
        rect = pygame.Rect(i * bw2, 47, bw2 - 2, 38)
        buttons.append((rect, tid, label))

    # Кнопки размера (правый край ряда 2)
    size_buttons = []
    labels = ['S', 'M', 'L']
    sx = WIN_W * 3 // 5 + 12
    for i, (key, px) in enumerate(SIZES.items()):
        rect = pygame.Rect(sx + i * 44, 52, 38, 28)
        size_buttons.append((rect, key, labels[i]))

    # Палитра (правый край, ряд 2)
    palette_rects = []
    px_start = sx + 3 * 44 + 16
    for i, color in enumerate(PALETTE):
        col = i % 5
        row = i // 5
        cx = px_start + col * 28
        cy = 52 + row * 24
        rect = pygame.Rect(cx - 11, cy, 22, 20)
        palette_rects.append((rect, color))

    return buttons, size_buttons, palette_rects


# ─── Отрисовка тулбара ────────────────────────────────────────────────────────

def draw_toolbar(screen, font, small_font,
                 buttons, size_buttons, palette_rects,
                 cur_mode, cur_color, cur_size_key):
    pygame.draw.rect(screen, BG_TOOLBAR, (0, 0, WIN_W, TOOLBAR_H))
    pygame.draw.line(screen, BORDER_COL, (0, 43), (WIN_W, 43), 1)
    pygame.draw.line(screen, BORDER_COL, (0, TOOLBAR_H - 1), (WIN_W, TOOLBAR_H - 1), 2)

    # Кнопки инструментов
    for rect, tid, label in buttons:
        col = BTN_ACTIVE if tid == cur_mode else BTN_NORMAL
        pygame.draw.rect(screen, col, rect, border_radius=5)
        txt = small_font.render(label, True, WHITE)
        screen.blit(txt, (rect.x + (rect.w - txt.get_width()) // 2,
                          rect.y + (rect.h - txt.get_height()) // 2))

    # Кнопки размера
    for rect, key, label in size_buttons:
        col = BTN_ACTIVE if key == cur_size_key else BTN_NORMAL
        pygame.draw.rect(screen, col, rect, border_radius=4)
        txt = small_font.render(label, True, WHITE)
        screen.blit(txt, (rect.x + (rect.w - txt.get_width()) // 2,
                          rect.y + (rect.h - txt.get_height()) // 2))

    # Палитра
    for rect, color in palette_rects:
        pygame.draw.rect(screen, color, rect, border_radius=3)
        if color == cur_color:
            pygame.draw.rect(screen, WHITE, rect.inflate(4, 4), 2, border_radius=4)

    # Текущий цвет — крупный квадрат
    preview_rect = pygame.Rect(WIN_W - 54, 50, 40, 40)
    pygame.draw.rect(screen, cur_color, preview_rect, border_radius=4)
    pygame.draw.rect(screen, GRAY, preview_rect, 1, border_radius=4)

    # Подсказка Ctrl+S
    hint = small_font.render("Ctrl+S — сохранить", True, (90, 90, 110))
    screen.blit(hint, (WIN_W - hint.get_width() - 8, 6))


# ─── Главный цикл ─────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint  |  Practice 12")
    clock = pygame.time.Clock()

    try:
        font       = pygame.font.SysFont("Segoe UI", 16)
        small_font = pygame.font.SysFont("Segoe UI", 12)
        text_font  = pygame.font.SysFont("Segoe UI", 20)
    except Exception:
        font       = pygame.font.SysFont(None, 18)
        small_font = pygame.font.SysFont(None, 14)
        text_font  = pygame.font.SysFont(None, 22)

    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    buttons, size_buttons, palette_rects = build_buttons()

    # ── Состояние ──────────────────────────────────────────────────────────────
    cur_color    = PALETTE[0]
    cur_mode     = 'pencil'
    cur_size_key = 2                    # 1/2/3 → SIZES
    drawing      = False
    last_pos     = None
    shape_start  = None

    # Текстовый инструмент
    text_active   = False
    text_pos      = (0, 0)             # позиция на холсте
    text_buffer   = ""
    cursor_blink  = 0                  # счётчик кадров для мигания

    def thickness():
        return SIZES[cur_size_key]

    while True:
        mx, my = pygame.mouse.get_pos()
        canvas_y = my - TOOLBAR_H       # Y в координатах холста

        # ── Обработка событий ─────────────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Клавиатура ────────────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                # Текстовый режим: перехватываем все символы
                if text_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # Фиксируем текст на холсте
                        surf = text_font.render(text_buffer, True, cur_color)
                        canvas.blit(surf, text_pos)
                        text_active  = False
                        text_buffer  = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
                    continue   # больше ничего не делаем пока пишем

                # Глобальные горячие клавиши
                ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
                if event.key == pygame.K_c and not ctrl:
                    canvas.fill(CANVAS_BG)
                elif event.key == pygame.K_s and ctrl:
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"canvas_{ts}.png"
                    pygame.image.save(canvas, fname)
                    pygame.display.set_caption(f"Paint  |  Сохранено: {fname}")
                elif event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_1:
                    cur_size_key = 1
                elif event.key == pygame.K_2:
                    cur_size_key = 2
                elif event.key == pygame.K_3:
                    cur_size_key = 3

            # ── Колесо мыши — не нужно, но оставим масштаб размера ────────────
            if event.type == pygame.MOUSEBUTTONDOWN and not text_active:
                if event.button == 4:
                    cur_size_key = min(3, cur_size_key + 1)
                    continue
                if event.button == 5:
                    cur_size_key = max(1, cur_size_key - 1)
                    continue

            # ── Клик мышью ────────────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not text_active:
                # Тулбар
                if my < TOOLBAR_H:
                    for rect, tid, label in buttons:
                        if rect.collidepoint(mx, my):
                            cur_mode = tid
                    for rect, key, label in size_buttons:
                        if rect.collidepoint(mx, my):
                            cur_size_key = key
                    for rect, color in palette_rects:
                        if rect.collidepoint(mx, my):
                            cur_color = color
                    continue

                # Холст
                if canvas_y < 0:
                    continue

                cx_pos = (mx, canvas_y)

                if cur_mode == 'fill':
                    flood_fill(canvas, cx_pos, cur_color)

                elif cur_mode == 'text':
                    text_active  = True
                    text_pos     = cx_pos
                    text_buffer  = ""
                    cursor_blink = 0

                elif cur_mode in SHAPE_TOOLS:
                    shape_start = cx_pos

                else:  # pencil / erase
                    drawing  = True
                    last_pos = cx_pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not text_active:
                if shape_start and cur_mode in SHAPE_TOOLS:
                    p2 = (mx, canvas_y)
                    draw_shape_final(canvas, cur_mode, shape_start, p2,
                                     cur_color, thickness())
                    shape_start = None
                else:
                    drawing  = False
                    last_pos = None

            if event.type == pygame.MOUSEMOTION and not text_active:
                if drawing and canvas_y >= 0:
                    cur_pos = (mx, canvas_y)
                    color   = CANVAS_BG if cur_mode == 'erase' else cur_color
                    t       = thickness()
                    if last_pos:
                        pygame.draw.line(canvas, color, last_pos, cur_pos, t)
                    pygame.draw.circle(canvas, color, cur_pos, t // 2 + 1)
                    last_pos = cur_pos

        # ── Отрисовка кадра ───────────────────────────────────────────────────
        screen.fill((20, 20, 28))
        screen.blit(canvas, (0, TOOLBAR_H))

        # Превью фигуры
        if shape_start and pygame.mouse.get_pressed()[0]:
            draw_shape_preview(screen, cur_mode, shape_start,
                               (mx, canvas_y), TOOLBAR_H, thickness())

        # Текстовый курсор и буфер
        if text_active:
            rendered = text_font.render(text_buffer, True, cur_color)
            tx = text_pos[0]
            ty = text_pos[1] + TOOLBAR_H
            screen.blit(rendered, (tx, ty))
            # мигающий курсор
            cursor_blink += 1
            if (cursor_blink // 30) % 2 == 0:
                cx_cur = tx + rendered.get_width() + 2
                pygame.draw.line(screen, cur_color,
                                 (cx_cur, ty),
                                 (cx_cur, ty + text_font.get_height()), 2)

        # Индикатор курсора (только не в текстовом режиме)
        if not text_active and my >= TOOLBAR_H:
            ind_col = CANVAS_BG if cur_mode == 'erase' else cur_color
            r = max(2, thickness() // 2 + 1)
            pygame.draw.circle(screen, ind_col, (mx, my), r, 1)

        draw_toolbar(screen, font, small_font,
                     buttons, size_buttons, palette_rects,
                     cur_mode, cur_color, cur_size_key)

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()
