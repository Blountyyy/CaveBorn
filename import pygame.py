import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))  # создаем окно
pygame.display.set_caption("My Game")          # название окна
clock = pygame.time.Clock()                    # создаем контроля FPS

player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (64, 80))  # масштабируем
player_rect = player_img.get_rect(center=(400, 300))


# Параметры физики
gravity = 0.5          # сила гравитации
jump_strength = -10     # сила прыжка (отрицательное значение — вверх)
player_y_velocity = 0   # текущая вертикальная скорость
on_ground = True        # стоит ли персонаж на земле

running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    keys = pygame.key.get_pressed()
    speed = 4  # Скорость движения

 # Горизонтальное движение
    if keys[pygame.K_a]:
        player_rect.x -= speed
    if keys[pygame.K_d]:
        player_rect.x += speed

    # Прыжок
    if keys[pygame.K_w] and on_ground:
        player_y_velocity = jump_strength
        on_ground = False

    # Применяем гравитацию
    player_y_velocity += gravity
    player_rect.y += player_y_velocity

    # Проверка на "землю"
    if player_rect.bottom >= 600:  # 600 — нижняя граница экрана
        player_rect.bottom = 600
        player_y_velocity = 0
        on_ground = True


  
    # Ограничения движения (границы экрана)
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > 800:  
        player_rect.right = 800
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > 600:  
        player_rect.bottom = 600
    

    screen.fill((30, 30, 30))  # Заполняем экран фоновым цветом
    screen.blit(player_img, player_rect)  # Рисуем игрока на экране
    pygame.display.flip()  # Обновляем экран

    clock.tick(60)  # Ограничиваем FPS до 60

pygame.quit()

    
    



