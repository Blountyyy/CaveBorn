import pygame
import os
import random

# Платформер с несколькими этажами и уровнями
# Контролы: A/D - влево/вправо, W - прыгнуть/подняться по лестнице, S - спуститься по лестнице
# ESC - выход, R - рестарт после гибели

pygame.init()

# --- Настройки окна ---
WIDTH, HEIGHT = 1280, 920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CaveBorn - Многоэтажный платформер")
clock = pygame.time.Clock()

# --- Пути к папкам ---
base_dir = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
assets_dir = os.path.join(base_dir, 'assets')
sound_dir = os.path.join(base_dir, 'sounds')

# --- Загрузка ассетов (с запасным вариантом) ---
def load_image(name, size=None, alpha=True):
    path = os.path.join(assets_dir, name)
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        # Запасной спрайт - простой прямоугольник
        surf = pygame.Surface(size or (50, 50), pygame.SRCALPHA)
        color = (200, 200, 200, 255)
        surf.fill(color)
        return surf

# Загрузка всех изображений
bg_img = load_image('bg.png', (WIDTH, HEIGHT), alpha=False)
player_img = load_image('player.png', (64, 80))
enemy_img_right = load_image('enemy.png', (64, 80))
enemy_img_left = pygame.transform.flip(enemy_img_right, True, False)
ladder_img = load_image('ladder.png', (80, 200))
coin_img = load_image('monet.png', (32, 32))  # Используем monet.png вместо coin.png
portal_img = load_image('portal.png', (80, 80))

# --- Звуки ---
def load_sound(name):
    path = os.path.join(sound_dir, name)
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

# Фоновая музыка
try:
    pygame.mixer.music.load(os.path.join(sound_dir, 'фон.mp3'))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except Exception:
    pass

walk_sound = load_sound('ходьба.mp3')
if walk_sound:
    walk_sound.set_volume(0.4)
jump_sound = load_sound('Прыжок.mp3')
if jump_sound:
    jump_sound.set_volume(0.4)
ladder_sound = load_sound('звуклестницы.mp3')
if ladder_sound:
    ladder_sound.set_volume(0.4)
portal_sound = load_sound('portal_sound.mp3')  # Добавьте звук для портала
coin_sound = load_sound('coin_sound.mp3')  # Добавьте звук для сбора монет

# --- Игровые константы ---
GRAVITY = 0.6
JUMP_STRENGTH = -12
PLAYER_SPEED = 6
ENEMY_SPEEDS = [-3, -2, 2, 3]
FLOOR_HEIGHT = 840
FLOOR_SPACING = 200

# --- Классы игры ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 32, y - 80, 64, 80)
        self.y_velocity = 0
        self.on_ground = True
        self.on_ladder = False
        self.health = 3
        self.coins_collected = 0
        self.current_floor = 1
        
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
    def jump(self):
        if self.on_ground and not self.on_ladder:
            self.y_velocity = JUMP_STRENGTH
            self.on_ground = False
            if jump_sound:
                jump_sound.play()
    
    def update(self, gravity=GRAVITY):
        if not self.on_ladder:
            self.y_velocity += gravity
            self.rect.y += self.y_velocity
            
        # Проверка нахождения на земле
        if self.rect.bottom >= FLOOR_HEIGHT - (self.current_floor - 1) * FLOOR_SPACING:
            self.rect.bottom = FLOOR_HEIGHT - (self.current_floor - 1) * FLOOR_SPACING
            self.y_velocity = 0
            self.on_ground = True
            
        # Границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Enemy:
    def __init__(self, x, y, speed, floor):
        self.rect = pygame.Rect(x - 32, y - 80, 64, 80)
        self.xv = speed
        self.yv = 0
        self.gravity = 0.4
        self.facing_right = speed > 0
        self.floor = floor
        self.img = enemy_img_right if speed > 0 else enemy_img_left
        
    def update(self):
        self.yv += self.gravity
        self.rect.y += self.yv
        self.rect.x += self.xv
        
        # Пол на текущем этаже
        current_floor_y = FLOOR_HEIGHT - (self.floor - 1) * FLOOR_SPACING
        
        if self.rect.bottom >= current_floor_y:
            self.rect.bottom = current_floor_y
            self.yv = 0
            
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.xv = -self.xv
            self.facing_right = not self.facing_right
            self.img = enemy_img_right if self.facing_right else enemy_img_left

class Level:
    def __init__(self, level_num, num_floors):
        self.level_num = level_num
        self.num_floors = num_floors
        self.portals = []
        self.ladders = []
        self.coins = []
        self.enemies = []
        self.setup_level()
        
    def setup_level(self):
        # Очищаем все
        self.portals.clear()
        self.ladders.clear()
        self.coins.clear()
        self.enemies.clear()
        
        # Лестницы между этажами
        for floor in range(1, self.num_floors):
            ladder_x = random.randint(200, WIDTH - 200)
            ladder_y = FLOOR_HEIGHT - (floor - 1) * FLOOR_SPACING
            self.ladders.append(pygame.Rect(ladder_x - 40, ladder_y - 200, 80, 200))
            
            # Вторая лестница для разнообразия
            if floor < self.num_floors - 1:
                ladder2_x = random.randint(200, WIDTH - 200)
                while abs(ladder2_x - ladder_x) < 200:  # Чтобы не были слишком близко
                    ladder2_x = random.randint(200, WIDTH - 200)
                self.ladders.append(pygame.Rect(ladder2_x - 40, ladder_y - 200, 80, 200))
        
        # Монеты на каждом этаже
        for floor in range(1, self.num_floors + 1):
            floor_y = FLOOR_HEIGHT - (floor - 1) * FLOOR_SPACING
            for _ in range(4):  # 4 монеты на этаж
                coin_x = random.randint(100, WIDTH - 100)
                coin_y = random.randint(floor_y - 180, floor_y - 50)
                self.coins.append({
                    'rect': pygame.Rect(coin_x, coin_y, 32, 32),
                    'floor': floor
                })
        
        # Враги (2 на этаж)
        for floor in range(1, self.num_floors + 1):
            floor_y = FLOOR_HEIGHT - (floor - 1) * FLOOR_SPACING
            for _ in range(2):  # 2 врага на этаж
                enemy_x = random.randint(100, WIDTH - 100)
                enemy_speed = random.choice(ENEMY_SPEEDS)
                self.enemies.append(Enemy(enemy_x, floor_y, enemy_speed, floor))
        
        # Портал на последнем этаже
        if self.num_floors > 1:
            portal_x = WIDTH // 2
            portal_y = FLOOR_HEIGHT - (self.num_floors - 1) * FLOOR_SPACING - 80
            self.portals.append(pygame.Rect(portal_x - 40, portal_y - 40, 80, 80))

# --- Инициализация игры ---
player = Player(400, FLOOR_HEIGHT)
current_level = 1
levels = [
    Level(1, 3),  # Уровень 1: 3 этажа
    Level(2, 4),  # Уровень 2: 4 этажа
    Level(3, 5)   # Уровень 3: 5 этажей
]
current_level_obj = levels[0]

# Статистика по монетам
level_coins = [0, 0, 0]  # Монеты собраны на каждом уровне

# Звук ходьбы
walk_sound_delay = 0
walk_sound_interval = 18
is_walking = False
ladder_sound_playing = False

# Шрифты
font = pygame.font.SysFont('arial', 28)
big_font = pygame.font.SysFont('arial', 64)
small_font = pygame.font.SysFont('arial', 22)

# Состояния игры
game_state = 'menu'  # 'menu', 'playing', 'level_complete', 'game_over', 'game_won'

# --- Вспомогательные функции ---
def reset_game():
    global player, current_level, current_level_obj, level_coins
    player = Player(400, FLOOR_HEIGHT)
    current_level = 1
    current_level_obj = levels[0]
    level_coins = [0, 0, 0]
    player.coins_collected = 0

def draw_floor_lines():
    """Рисует линии этажей для визуализации"""
    for floor in range(1, current_level_obj.num_floors + 1):
        floor_y = FLOOR_HEIGHT - (floor - 1) * FLOOR_SPACING
        pygame.draw.line(screen, (100, 100, 100, 100), (0, floor_y), (WIDTH, floor_y), 2)
        
        # Номер этажа
        floor_text = small_font.render(f'Этаж {floor}', True, (150, 150, 150))
        screen.blit(floor_text, (20, floor_y - 30))

# --- Главный игровой цикл ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if game_state == 'menu' and event.key == pygame.K_RETURN:
                game_state = 'playing'
            if game_state == 'game_over' and event.key == pygame.K_r:
                reset_game()
                game_state = 'playing'
            if game_state == 'level_complete' and event.key == pygame.K_SPACE:
                if current_level < 3:
                    current_level += 1
                    current_level_obj = levels[current_level - 1]
                    player.current_floor = 1
                    player.rect.midbottom = (400, FLOOR_HEIGHT)
                    game_state = 'playing'
                else:
                    game_state = 'game_won'
            if game_state == 'game_won' and event.key == pygame.K_r:
                reset_game()
                game_state = 'menu'

    keys = pygame.key.get_pressed()

    # Меню
    if game_state == 'menu':
        screen.blit(bg_img, (0, 0))
        title = big_font.render('CAVEBORN', True, (255, 255, 255))
        subtitle = font.render('Многоэтажный платформер', True, (200, 200, 255))
        instr1 = small_font.render('Управление: A/D - движение, W - прыжок/подъем по лестнице, S - спуск по лестнице', True, (255, 255, 255))
        instr2 = small_font.render('Цель: Собрать монеты и дойти до портала на верхнем этаже', True, (255, 255, 255))
        start = font.render('Нажмите ENTER для начала игры', True, (100, 255, 100))
        
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        screen.blit(instr1, instr1.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        screen.blit(instr2, instr2.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
        screen.blit(start, start.get_rect(center=(WIDTH//2, HEIGHT//2 + 120)))
        
        pygame.display.flip()
        clock.tick(30)
        continue

    # Игровой процесс
    if game_state == 'playing':
        # Проверка нахождения на лестнице
        player.on_ladder = False
        for ladder in current_level_obj.ladders:
            if player.rect.colliderect(ladder):
                # Проверяем, находится ли игрок на правильном этаже для этой лестницы
                ladder_bottom_y = ladder.bottom
                player_floor_y = FLOOR_HEIGHT - (player.current_floor - 1) * FLOOR_SPACING
                
                if abs(ladder_bottom_y - player_floor_y) < 50:
                    player.on_ladder = True
                    player.y_velocity = 0
                    player.on_ground = False
                    break

        # Управление игроком
        was_walking = is_walking
        is_walking = False
        
        # Горизонтальное движение
        if keys[pygame.K_a]:
            player.move(-PLAYER_SPEED, 0)
            is_walking = True
        if keys[pygame.K_d]:
            player.move(PLAYER_SPEED, 0)
            is_walking = True
            
        # Прыжок
        if keys[pygame.K_w] and not player.on_ladder:
            player.jump()
            
        # Движение по лестнице
        if player.on_ladder:
            if keys[pygame.K_w]:
                player.move(0, -4)
                # Проверяем переход на следующий этаж
                if player.rect.bottom < FLOOR_HEIGHT - player.current_floor * FLOOR_SPACING + 50:
                    player.current_floor += 1
            if keys[pygame.K_s]:
                player.move(0, 4)
                # Проверяем переход на предыдущий этаж
                if player.rect.bottom > FLOOR_HEIGHT - (player.current_floor - 2) * FLOOR_SPACING - 50 and player.current_floor > 1:
                    player.current_floor -= 1
                    
            # Звук лестницы
            if not ladder_sound_playing and ladder_sound:
                ladder_sound.play(-1)
                ladder_sound_playing = True
        else:
            if ladder_sound_playing and ladder_sound:
                ladder_sound.stop()
                ladder_sound_playing = False
                
        # Звук ходьбы
        if is_walking and player.on_ground and not player.on_ladder and walk_sound:
            walk_sound_delay += 1
            if walk_sound_delay >= walk_sound_interval:
                walk_sound.play()
                walk_sound_delay = 0
        else:
            walk_sound_delay = walk_sound_interval
            
        # Обновление физики игрока
        player.update()
        
        # Обновление врагов
        for enemy in current_level_obj.enemies[:]:
            enemy.update()
            
            # Столкновение с игроком
            if player.rect.colliderect(enemy.rect) and enemy.floor == player.current_floor:
                # Отталкивание
                if player.rect.centerx < enemy.rect.centerx:
                    player.move(-40, 0)
                else:
                    player.move(40, 0)
                    
                player.health -= 1
                if player.health <= 0:
                    game_state = 'game_over'
                    
        # Сбор монет
        for coin in current_level_obj.coins[:]:
            if player.rect.colliderect(coin['rect']) and coin['floor'] == player.current_floor:
                current_level_obj.coins.remove(coin)
                player.coins_collected += 10
                level_coins[current_level - 1] += 10
                if coin_sound:
                    coin_sound.play()
                    
        # Проверка портала
        for portal in current_level_obj.portals:
            if player.rect.colliderect(portal) and player.current_floor == current_level_obj.num_floors:
                if portal_sound:
                    portal_sound.play()
                game_state = 'level_complete'
                
        # --- Отрисовка ---
        screen.blit(bg_img, (0, 0))
        
        # Рисуем линии этажей
        draw_floor_lines()
        
        # Рисуем лестницы
        for ladder in current_level_obj.ladders:
            screen.blit(ladder_img, ladder)
            
        # Рисуем монеты
        for coin in current_level_obj.coins:
            if coin['floor'] == player.current_floor:
                screen.blit(coin_img, coin['rect'])
                
        # Рисуем врагов на текущем этаже
        for enemy in current_level_obj.enemies:
            if enemy.floor == player.current_floor:
                screen.blit(enemy.img, enemy.rect)
                
        # Рисуем порталы
        for portal in current_level_obj.portals:
            screen.blit(portal_img, portal)
            
        # Рисуем игрока
        screen.blit(player_img, player.rect)
        
        # UI
        hp_text = font.render(f'Здоровье: {player.health}', True, (255, 100, 100))
        score_text = font.render(f'Монеты: {player.coins_collected}', True, (255, 215, 0))
        level_text = font.render(f'Уровень: {current_level}/3  Этаж: {player.current_floor}/{current_level_obj.num_floors}', True, (100, 200, 255))
        coins_level_text = small_font.render(f'Монеты на уровне: {level_coins[current_level-1]}', True, (255, 215, 0))
        
        screen.blit(hp_text, (20, 20))
        screen.blit(score_text, (20, 60))
        screen.blit(level_text, (20, 100))
        screen.blit(coins_level_text, (20, 140))
        
        # Подсказки управления
        controls_text = small_font.render('A/D - двигаться, W - прыжок/подъем, S - спуск, ESC - выход', True, (200, 200, 200))
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
        continue
        
    # Уровень завершен
    if game_state == 'level_complete':
        screen.blit(bg_img, (0, 0))
        
        if current_level < 3:
            message = big_font.render(f'УРОВЕНЬ {current_level} ПРОЙДЕН!', True, (100, 255, 100))
            next_level = font.render(f'Нажмите ПРОБЕЛ для перехода на уровень {current_level + 1}', True, (255, 255, 255))
            stats = font.render(f'Монеты собрано на этом уровне: {level_coins[current_level-1]}', True, (255, 215, 0))
            
            screen.blit(message, message.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
            screen.blit(stats, stats.get_rect(center=(WIDTH//2, HEIGHT//2)))
            screen.blit(next_level, next_level.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        else:
            message = big_font.render('ВСЕ УРОВНИ ПРОЙДЕНЫ!', True, (255, 215, 0))
            stats = font.render(f'Общее количество монет: {player.coins_collected}', True, (255, 215, 0))
            next_level = font.render('Нажмите ПРОБЕЛ для просмотра результатов', True, (255, 255, 255))
            
            screen.blit(message, message.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
            screen.blit(stats, stats.get_rect(center=(WIDTH//2, HEIGHT//2)))
            screen.blit(next_level, next_level.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
            
        pygame.display.flip()
        clock.tick(30)
        continue
        
    # Игра выиграна
    if game_state == 'game_won':
        screen.blit(bg_img, (0, 0))
        
        congrats = big_font.render('ПОБЕДА!', True, (255, 215, 0))
        total_coins = font.render(f'Всего собрано монет: {player.coins_collected}', True, (255, 255, 255))
        
        # Статистика по уровням
        level1_stats = small_font.render(f'Уровень 1: {level_coins[0]} монет', True, (200, 200, 200))
        level2_stats = small_font.render(f'Уровень 2: {level_coins[1]} монет', True, (200, 200, 200))
        level3_stats = small_font.render(f'Уровень 3: {level_coins[2]} монет', True, (200, 200, 200))
        
        restart = font.render('Нажмите R для начала новой игры', True, (100, 255, 100))
        
        screen.blit(congrats, congrats.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))
        screen.blit(total_coins, total_coins.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        screen.blit(level1_stats, level1_stats.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        screen.blit(level2_stats, level2_stats.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
        screen.blit(level3_stats, level3_stats.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        screen.blit(restart, restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 140)))
        
        pygame.display.flip()
        clock.tick(30)
        continue
        
    # Игра проиграна
    if game_state == 'game_over':
        screen.blit(bg_img, (0, 0))
        
        game_over = big_font.render('ИГРА ОКОНЧЕНА', True, (255, 50, 50))
        final_score = font.render(f'Собрано монет: {player.coins_collected}', True, (255, 255, 255))
        restart = font.render('Нажмите R для рестарта', True, (255, 255, 255))
        
        screen.blit(game_over, game_over.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        screen.blit(final_score, final_score.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        screen.blit(restart, restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
        
        pygame.display.flip()
        clock.tick(30)
        continue

pygame.quit()