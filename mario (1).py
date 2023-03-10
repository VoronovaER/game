import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        try:
            image = image.convert_alpha()
        except pygame.error:
            pass
    return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)


    def move(self, x, y, level_map):
        global money
        global level
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in tiles_group:
            camera.apply(sprite)
        if level_map[y][x] == '*':
            print('Ой! Вы умерли.')
            print(f'У вас {money} денег.')
            money = 0
            between_levels()
        if level_map[y][x] == 'e':
            print('Ура! Вы прошли уровень!')
            print(f'У вас {money} денег.')
            level += 1
            between_levels(money)
        if level_map[y][x] == '$':
            print('Ура! Вы нашли монетку.')
            money += 1
            level_map[y] = level_map[y][:x] + '.' + level_map[y][x + 1:]


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '*':
                Tile('rock', x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y)
                Tile('treasure', x, y)
            elif level[y][x] == 'e':
                Tile('door', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def between_levels(money=0):
    print('Хотите продолжить игру?')
    a = input()
    while True:
        if a.lower() == 'да':
            main()
            break
        elif a.lower() == 'нет':
            print('Жаль)')
            terminate()
            break
        else:
            print('Неверный ввод. Введите только да или нет')
            a = input()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["The Mase. Mario version", "",
                  f"Level {level}"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def move(hero, movement, level_map, max_x, max_y):
    x, y = hero.pos
    if movement == "up" or movement == "w":
        if y > 0 and level_map[y - 1][x] != '#':
            hero.move(x, y - 1, level_map)
    elif movement == "down" or movement == "s":
        if y < max_y and level_map[y + 1][x] != '#':
            hero.move(x, y + 1, level_map)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] != '#':
            hero.move(x - 1, y, level_map)
    if movement == "right":
        if x < max_x and level_map[y][x + 1] != '#':
            hero.move(x + 1, y, level_map)


pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("Перемещение героя")
screen_size = WIDTH, HEIGHT = (500, 500)
screen = pygame.display.set_mode(screen_size)
FPS = 50
money = 0
tile_images = {'wall': load_image('box.png'),
               'empty': load_image('grass.png'),
               'rock': load_image('gray_rock.png'),
               'treasure': load_image('treasure.png'),
               'door': load_image('door.png')}

player_image = load_image('mar.png')

tile_width = tile_height = 50

player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
camera = Camera()
level = 1


def main():
    global level
    if level > 3:
        print("Вы прошли все уровни!")
        level = 1
        between_levels()
    start_screen()
    try:
        if int(level) == 1:
            levelname = 'map.map'
        elif int(level) == 2:
            levelname = 'level2'
        elif int(level) == 3:
            levelname = 'level3'
        else:
            raise ValueError
    except ValueError:
        terminate()

    level_map = load_level(levelname)
    hero, max_x, max_y = generate_level(level_map)
    camera.update(hero)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    move(hero, "up", level_map, max_x, max_y)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    move(hero, "down", level_map, max_x, max_y)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    move(hero, "left", level_map, max_x, max_y)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    move(hero, "right", level_map, max_x, max_y)
        screen.fill(pygame.Color("black"))
        tiles_group.draw(screen)
        player_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
main()