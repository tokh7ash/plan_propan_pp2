import pygame, sys, os, random
from pygame.locals import *

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

# Предзаданные цвета
BLUE   = (0, 0, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)

# Настройки экрана
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# Папка скрипта — чтобы картинки всегда находились независимо от рабочей директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

# Шрифт для отображения счёта монет
font = pygame.font.SysFont("Verdana", 20)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Загружаем изображение врага через BASE_DIR
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Enemy.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        # Движение врага вниз по экрану
        self.rect.move_ip(0, 10)
        # Если враг вышел за нижний край — сбрасываем наверх
        if (self.rect.bottom > 600):
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Загружаем изображение игрока через BASE_DIR
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Player.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def update(self):
        # Получаем нажатые клавиши
        pressed_keys = pygame.key.get_pressed()

        # Движение влево — только если не у левого края
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
        # Движение вправо — только если не у правого края
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    """Монета, которая случайно появляется на дороге и движется вниз."""

    def __init__(self):
        super().__init__()
        # Рисуем монету как жёлтый круг с символом $
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (14, 14), 13)
        pygame.draw.circle(self.image, (180, 140, 0), (14, 14), 13, 2)
        label = font.render("$", True, (100, 70, 0))
        self.image.blit(label, label.get_rect(center=(14, 14)))

        self.rect = self.image.get_rect()
        # Случайная позиция по горизонтали, появляется за верхним краем
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -14)
        # Случайная скорость падения монеты
        self.speed = random.randint(4, 8)

    def move(self):
        # Монета движется вниз
        self.rect.move_ip(0, self.speed)
        # Если монета вышла за нижний край — удаляем её
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Создаём игрока и врага (как в оригинале)
P1 = Player()
E1 = Enemy()

# Группа спрайтов для монет — удобно для проверки столкновений
coin_group = pygame.sprite.Group()

# Счётчик собранных монет
coins_collected = 0

# Таймер для появления монет каждые 2 секунды
SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 2000)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Каждые 2 секунды появляется новая монета (70% шанс)
        if event.type == SPAWN_COIN:
            if random.random() < 0.7:
                coin_group.add(Coin())

    # Обновляем позицию игрока по нажатым клавишам
    P1.update()
    # Двигаем врага вниз
    E1.move()
    # Двигаем все монеты вниз
    for coin in coin_group:
        coin.move()

    # Проверка столкновения игрока и врага — конец игры
    if P1.rect.colliderect(E1.rect):
        print(f"Столкновение! Игра окончена. Монет собрано: {coins_collected}")
        pygame.quit()
        sys.exit()

    # Проверка столкновения игрока с монетами
    # True — удалять монету при столкновении
    hit_coins = pygame.sprite.spritecollide(P1, coin_group, True)
    coins_collected += len(hit_coins)  # увеличиваем счётчик

    # Перерисовываем фон (как в оригинале)
    DISPLAYSURF.fill(WHITE)

    # Рисуем монеты
    for coin in coin_group:
        coin.draw(DISPLAYSURF)

    # Рисуем игрока и врага (как в оригинале)
    P1.draw(DISPLAYSURF)
    E1.draw(DISPLAYSURF)

    # Отображаем счётчик монет в правом верхнем углу
    score_surf = font.render(f"Монет: {coins_collected}", True, (180, 140, 0))
    DISPLAYSURF.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))

    pygame.display.update()
    FramePerSec.tick(FPS)