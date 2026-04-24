import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Paint с ластиком (ПКМ)")
    clock = pygame.time.Clock()

    canvas = pygame.Surface((640, 480))
    canvas_color = (0, 0, 0)  # Цвет фона холста
    canvas.fill(canvas_color)

    radius = 5
    drawing = False
    erasing = False
    last_pos = None
    mode = 'blue'

    # Режим прямоугольника
    rect_mode = False        # True — рисуем прямоугольник
    rect_start = None        # Точка начала прямоугольника (где нажали ЛКМ)

    colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255)
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: mode = 'red'
                elif event.key == pygame.K_g: mode = 'green'
                elif event.key == pygame.K_b: mode = 'blue'
                elif event.key == pygame.K_c:
                    canvas.fill(canvas_color)
                elif event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_t:  # T — переключить режим прямоугольника
                    rect_mode = not rect_mode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    if rect_mode:
                        rect_start = event.pos   # запоминаем начальную точку
                    else:
                        drawing = True
                elif event.button == 3:  # ПКМ - Ластик
                    erasing = True
                elif event.button == 4:  # Колесо вверх
                    radius = min(50, radius + 1)
                elif event.button == 5:  # Колесо вниз
                    radius = max(1, radius - 1)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if rect_mode and rect_start:
                        # Отпустили кнопку — рисуем финальный прямоугольник на холсте
                        x = min(rect_start[0], event.pos[0])
                        y = min(rect_start[1], event.pos[1])
                        w = abs(event.pos[0] - rect_start[0])
                        h = abs(event.pos[1] - rect_start[1])
                        pygame.draw.rect(canvas, colors[mode], (x, y, w, h), 2)
                        rect_start = None
                    else:
                        drawing = False
                        last_pos = None
                elif event.button == 3:
                    erasing = False
                    last_pos = None

            if event.type == pygame.MOUSEMOTION:
                if drawing or erasing:
                    current_pos = event.pos
                    # Если стираем, используем цвет фона, иначе текущий цвет
                    color = canvas_color if erasing else colors[mode]

                    if last_pos:
                        pygame.draw.line(canvas, color, last_pos, current_pos, radius * 2)
                        pygame.draw.circle(canvas, color, current_pos, radius)
                    else:
                        pygame.draw.circle(canvas, color, current_pos, radius)

                    last_pos = current_pos

        screen.fill((30, 30, 30))
        screen.blit(canvas, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # Превью прямоугольника — показываем пока держим ЛКМ в режиме rect
        if rect_mode and rect_start:
            x = min(rect_start[0], mouse_pos[0])
            y = min(rect_start[1], mouse_pos[1])
            w = abs(mouse_pos[0] - rect_start[0])
            h = abs(mouse_pos[1] - rect_start[1])
            pygame.draw.rect(screen, colors[mode], (x, y, w, h), 2)

        indicator_color = (255, 255, 255) if erasing else colors[mode]
        pygame.draw.circle(screen, indicator_color, mouse_pos, radius, 1)

        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    main()