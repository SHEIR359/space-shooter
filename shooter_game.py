import pygame
from pygame import *
from random import randint
from time import time as timer

# Инициализация Pygame
pygame.init()

# Загрузка изображений
img_back = "galaxy.jpg"
img_bullet = "bullet.png"
img_hero = "rocket.png"
img_enemy = "ufo.png"
img_ast = "asteroid.png"

# Настройки окна
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")
background = transform.scale(image.load(img_back), (win_width, win_height))
# Подгрузка шрифтов
font.init()
font1 = font.Font(None, 80)
font2 = font.Font(None, 36)

# Загрузка музыки и звуков
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play(-1)
fire_sound = mixer.Sound('fire.ogg')

# Переменные игры
score = 0
goal = 20
lost = 0
max_lost = 10
life = 3
coins = 0  # Количество монет

# Класс-родитель для спрайтов
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

# Создание спрайтов
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(1, 3):
    asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(asteroid)

bullets = sprite.Group()

# Переменные для игры
finish = False
rel_time = False
num_fire = 0

# Основной цикл игры
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and not rel_time:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True

    if not finish:
        window.blit(background, (0, 0))

        # Движение спрайтов
        ship.update()
        monsters.update()
        asteroids.update()
        bullets.update()

        # Отрисовка спрайтов
        ship.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)

        # Перезарядка
        if rel_time:
            now_time = timer()
            if now_time - last_time < 3:
                reload = font2.render('Wait, reload...', 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                rel_time = False

        # Проверка столкновений
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        collides1 = sprite.groupcollide(asteroids, bullets, True, True)
        for c in collides1:
            asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(asteroid)
            num_fire -= 1

        # Проверка столкновения с врагами
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1

        # Проигрыш
        if life == 0 or lost >= max_lost:
            finish = True
            coins += score // 2  # Преобразование очков в монеты (2 очка = 1 монета) # Пустой фон при проигрыше
            lose_text = font1.render('YOU LOSE!', True, (255, 0, 0))
            window.blit(lose_text, (200, 200))
            coins_text = font2.render(f'Monets: {coins}', True, (255, 255, 255))
            window.blit(coins_text, (250, 300))
            play_button = font2.render('Play Again', True, (255, 255, 255))
            shop_button = font2.render('Shop', True, (255, 255, 255))
            window.blit(play_button, (250, 350))
            window.blit(shop_button, (250, 400))
            display.update()

            # Ожидание нажатия кнопки для перезапуска или перехода в магазин
            waiting = True
            while waiting:
                for e in event.get():
                    if e.type == QUIT:
                        exit()
                    elif e.type == KEYDOWN:
                        if e.key == K_RETURN:  # Нажатие Enter для перезапуска
                            waiting = False
                        elif e.key == K_s:  # Нажатие S для перехода в магазин
                            waiting = False
                            # Здесь можно добавить логику для открытия магазина
        # Отображение текста на экране
        text = font2.render("Score: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Lost: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        # Отображение жизней
        life_color = (0, 150, 0) if life == 3 else (150, 150, 0) if life == 2 else (150, 0, 0)
        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (10, 100))

        # Обновление экрана
        display.update()
        time.delay(50)  # Задержка для управления частотой кадров