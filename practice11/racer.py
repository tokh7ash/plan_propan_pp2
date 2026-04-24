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

# --- НОВОЕ: Настройки весов монет ---
# Каждая монета имеет тип (tier), вес (weight, для random.choices),
# стоимость (value) и цвет. Чем выше tier — тем редче монета, но больше очков.
COIN_TIERS = [
    {"tier": "bronze", "value": 1,  "color": (180, 100, 40),  "border": (120, 60, 20),   "weight": 60},
    {"tier": "silver", "value": 3,  "color": (192, 192, 192), "border": (140, 140, 140), "weight": 30},
    {"tier": "gold",   "value": 10, "color": (255, 215, 0),   "border": (180, 140, 0),   "weight": 10},
]

# --- НОВОЕ: Настройки ускорения врага ---
# Каждые N монет скорость врага увеличивается на ENEMY_SPEED_STEP пикселей
COINS_PER_SPEEDUP = 10   # порог монет для ускорения
ENEMY_SPEED_STEP  = 2    # на сколько пикселей ускоряется враг при каждом пороге
ENEMY_BASE_SPEED  = 10   # базовая скорость врага (оригинальная)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Загружаем изображение врага через BASE_DIR
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Enemy.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

        # --- НОВОЕ: текущая скорость врага (меняется динамически) ---
        self.speed = ENEMY_BASE_SPEED

    def move(self):
        # Движение врага вниз по экрану с текущей скоростью
        self.rect.move_ip(0, self.speed)
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
    """Монета, которая случайно появляется на дороге и движется вниз.

    --- ИЗМЕНЕНО: теперь монеты имеют разные веса (тиры).
    Тир выбирается случайно с учётом весов из COIN_TIERS:
      - bronze (60%) — стоит 1 очко
      - silver (30%) — стоит 3 очка
      - gold   (10%) — стоит 10 очков
    """

    def __init__(self):
        super().__init__()

        # --- НОВОЕ: выбираем тир монеты случайно по весам ---
        tier_data = random.choices(
            COIN_TIERS,
            weights=[t["weight"] for t in COIN_TIERS],
            k=1
        )[0]

        # Сохраняем стоимость монеты для подсчёта очков
        self.value = tier_data["value"]

        # Рисуем монету как круг с цветом выбранного тира и символом $
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(self.image, tier_data["color"],  (14, 14), 13)
        pygame.draw.circle(self.image, tier_data["border"], (14, 14), 13, 2)
        label = font.render("$", True, (60, 40, 0))
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

# --- НОВОЕ: отслеживаем последний порог ускорения врага ---
# При старте враг ещё не ускорялся ни разу
last_speedup_threshold = 0

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

    # --- ИЗМЕНЕНО: прибавляем стоимость каждой подобранной монеты (не просто +1) ---
    for coin in hit_coins:
        coins_collected += coin.value

    # --- НОВОЕ: проверяем, нужно ли ускорить врага ---
    # Вычисляем текущий порог (сколько раз преодолён COINS_PER_SPEEDUP)
    current_threshold = coins_collected // COINS_PER_SPEEDUP
    if current_threshold > last_speedup_threshold:
        # Враг ускоряется на каждое новое кратное COINS_PER_SPEEDUP
        steps = current_threshold - last_speedup_threshold
        E1.speed += steps * ENEMY_SPEED_STEP
        last_speedup_threshold = current_threshold
        print(f"Враг ускорился! Новая скорость: {E1.speed} (монет: {coins_collected})")

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

    # --- НОВОЕ: отображаем текущую скорость врага под счётчиком монет ---
    speed_surf = font.render(f"Скорость: {E1.speed}", True, RED)
    DISPLAYSURF.blit(speed_surf, (SCREEN_WIDTH - speed_surf.get_width() - 10, 35))

    pygame.display.update()
    FramePerSec.tick(FPS)