import pygame

pygame.init()

# --- Настройки окна ---
screen = pygame.display.set_mode((1280, 920))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# --- Загрузка изображений ---
bg_img = pygame.image.load("assets/bg.png").convert()
bg_img = pygame.transform.scale(bg_img, (1280, 920))

player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (64, 80))

# --- Враг (x2) ---
enemy_img_right = pygame.image.load("assets/enemy.png").convert_alpha()
enemy_img_right = pygame.transform.scale(enemy_img_right, (64, 80))
enemy_img_left = pygame.transform.flip(enemy_img_right, True, False)

# --- Игрок ---
player_rect = player_img.get_rect(center=(400, 300))
player_y_velocity = 0
gravity = 0.5
jump_strength = -10
on_ground = True
speed = 4

# --- Враг 1 ---
enemy1_img = enemy_img_right
enemy1_rect = enemy1_img.get_rect(center=(200, 100))
enemy1_y_velocity = 0
enemy1_x_velocity = 3
enemy1_gravity = 0.4
enemy1_on_ground = False
enemy1_facing_right = True

# --- Враг 2 ---
enemy2_img = enemy_img_left
enemy2_rect = enemy2_img.get_rect(center=(600, 100))
enemy2_y_velocity = 0
enemy2_x_velocity = -2
enemy2_gravity = 0.4
enemy2_on_ground = False
enemy2_facing_right = False

# --- Главный цикл ---
running = True
while running:
    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    # --- Движение игрока ---
    if keys[pygame.K_a]:
        player_rect.x -= speed
    if keys[pygame.K_d]:
        player_rect.x += speed
    if keys[pygame.K_w] and on_ground:
        player_y_velocity = jump_strength
        on_ground = False

    # --- Физика игрока ---
    player_y_velocity += gravity
    player_rect.y += player_y_velocity

    if player_rect.bottom >= 920:
        player_rect.bottom = 920
        player_y_velocity = 0
        on_ground = True

    # --- Ограничения по экрану ---
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > 1280:
        player_rect.right = 1280

    # === ВРАГ 1 ===
    enemy1_y_velocity += enemy1_gravity
    enemy1_rect.y += enemy1_y_velocity
    enemy1_rect.x += enemy1_x_velocity

    if enemy1_rect.bottom >= 920:
        enemy1_rect.bottom = 920
        enemy1_y_velocity = 0
        enemy1_on_ground = True
    else:
        enemy1_on_ground = False

    if enemy1_rect.left <= 0 or enemy1_rect.right >= 1280:
        enemy1_x_velocity = -enemy1_x_velocity
        enemy1_facing_right = not enemy1_facing_right
        enemy1_img = enemy_img_right if enemy1_facing_right else enemy_img_left

    # === ВРАГ 2 ===
    enemy2_y_velocity += enemy2_gravity
    enemy2_rect.y += enemy2_y_velocity
    enemy2_rect.x += enemy2_x_velocity

    if enemy2_rect.bottom >= 920:
        enemy2_rect.bottom = 920
        enemy2_y_velocity = 0
        enemy2_on_ground = True
    else:
        enemy2_on_ground = False

    if enemy2_rect.left <= 0 or enemy2_rect.right >= 1280:
        enemy2_x_velocity = -enemy2_x_velocity
        enemy2_facing_right = not enemy2_facing_right
        enemy2_img = enemy_img_right if enemy2_facing_right else enemy_img_left

    # --- Отрисовка ---
    screen.blit(bg_img, (0, 0))
    screen.blit(player_img, player_rect)
    screen.blit(enemy1_img, enemy1_rect)
    screen.blit(enemy2_img, enemy2_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
