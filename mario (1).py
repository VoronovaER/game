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

    def move(self, x, y, level_map, screen):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in tiles_group:
            camera.apply(sprite)
        check(level_map, screen, x, y)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self):
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


def end(screen):
    screen.fill(pygame.Color("black"))
    intro_text = ["You died. Wanna try again?"]
    font = pygame.font.Font(None, 30)
    text_coord = 80
    for line in intro_text:
        string_rendered = font.render(line, False, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        pygame.draw.rect(screen, pygame.Color('white'), (70, 250, 100, 75), 8)
        pygame.draw.rect(screen, pygame.Color('white'), (210, 250, 100, 75), 8)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
                return
        pygame.display.flip()


def between_levels():
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


def start_screen(screen, clock):
    intro_text = ["The Mase. Mario version", "",
                  f"Level {level}",
                  f"{money} money"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, False, pygame.Color('red'))
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


def move(hero, movement, level_map, max_x, max_y, screen):
    x, y = hero.pos
    if movement == "up" or movement == "w":
        if y > 0 and level_map[y - 1][x] != '#':
            hero.move(x, y - 1, level_map, screen)
    elif movement == "down" or movement == "s":
        if y < max_y and level_map[y + 1][x] != '#':
            hero.move(x, y + 1, level_map, screen)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] != '#':
            hero.move(x - 1, y, level_map, screen)
    if movement == "right":
        if x < max_x and level_map[y][x + 1] != '#':
            hero.move(x + 1, y, level_map, screen)


def check(level_map, screen, x, y):
    global money, level
    if level_map[y][x] == '*':
        money = 0
        end(screen)
    if level_map[y][x] == 'e':
        level += 1
        main()
    if level_map[y][x] == '$':
        money += 1
        level_map[y] = level_map[y][:x] + '.' + level_map[y][x + 1:]


FPS = 50
money = 0
tile_images = {'wall': load_image('box.png'),
               'empty': load_image('grass.png'),
               'rock': load_image('gray_rock.png'),
               'treasure': load_image('treasure.png'),
               'door': load_image('door.png')}

player_image = load_image('mar.png')
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
level = 1
camera = Camera()
screen_size = WIDTH, HEIGHT = (500, 500)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Перемещение героя")
    screen = pygame.display.set_mode(screen_size)
    player = None
    global level
    if level > 3:
        level = 1
        main()
    start_screen(screen, clock)
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
    camera.update()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    move(hero, "up", level_map, max_x, max_y, screen)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    move(hero, "down", level_map, max_x, max_y, screen)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    move(hero, "left", level_map, max_x, max_y, screen)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    move(hero, "right", level_map, max_x, max_y, screen)
        screen.fill(pygame.Color("black"))
        tiles_group.draw(screen)
        player_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
