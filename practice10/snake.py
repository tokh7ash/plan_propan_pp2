import pygame
import time
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game: Levels & Speed")

# Цвета
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Параметры змейки
SNAKE_BLOCK = 10
clock = pygame.time.Clock()

# Шрифты для счета и уровней
score_font = pygame.font.SysFont("Segoe UI", 25)
level_font = pygame.font.SysFont("Segoe UI", 25, bold=True)

def display_status(score, level):
    """Отображает текущий счет и уровень на экране."""
    value = score_font.render(f"Score: {score}", True, YELLOW)
    lvl_value = level_font.render(f"Level: {level}", True, WHITE)
    screen.blit(value, [10, 10])
    screen.blit(lvl_value, [WIDTH - 100, 10])

def draw_snake(snake_block, snake_list):
    """Рисует каждый сегмент змейки."""
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])

def game_loop():
    game_over = False
    game_close = False

    # Начальные координаты змейки
    x1 = WIDTH / 2
    y1 = HEIGHT / 2
    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1
    
    # Стартовые показатели
    score = 0
    level = 1
    speed = 15 

    # Генерация первой еды
    foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
    foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0

    while not game_over:

        while game_close:
            screen.fill(BLUE)
            msg = score_font.render("Game Over! Press C-Play Again or Q-Quit", True, RED)
            screen.blit(msg, [WIDTH / 6, HEIGHT / 3])
            display_status(score, level)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = SNAKE_BLOCK
                    x1_change = 0

        # 1. Проверка столкновения со стенами
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
        
        x1 += x1_change
        y1 += y1_change
        screen.fill(BLACK)
        
        # Рисуем еду
        pygame.draw.rect(screen, RED, [foodx, foody, SNAKE_BLOCK, SNAKE_BLOCK])
        
        # Логика роста змейки
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Проверка столкновения змейки с самой собой
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(SNAKE_BLOCK, snake_list)
        display_status(score, level)

        pygame.display.update()

        # 2. Логика поедания еды
        if x1 == foodx and y1 == foody:
            # Генерация новой еды так, чтобы она не попала на змейку
            foodx = round(random.randrange(0, WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
            foody = round(random.randrange(0, HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
            length_of_snake += 1
            score += 1
            
            # 3. Добавление уровней: каждые 5 очков — новый уровень
            if score % 5 == 0:
                level += 1
                speed += 3 # 4. Увеличение скорости при переходе на новый уровень

        clock.tick(speed)

    pygame.quit()
    quit()

game_loop()