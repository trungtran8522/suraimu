import pygame
import tcod
import itertools
import random

# TODO
# 1. Actually complete the thing (never going to be done)
# 2. Implement the actual boss (done)
# 3. Adding music (scrapped)
# 4. Failing life. (done)

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 20)

clock = pygame.time.Clock()

# Screen size
SCRWIDTH = 1024
SCRHEIGHT = 1024
screen = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))

BRICK_WIDTH = 32
BRICK_HEIGHT = 32

# fill initial screen with black
screen.fill((0, 0, 0))

# placeholder tiles creation
wall = pygame.Surface((32, 32))
wall.fill((255, 255, 255))

floor = pygame.Surface((32, 32))
floor.fill((128, 255, 128))

# actual tiles creation
wallbg = pygame.image.load('assets/wall.png')
floorbg = pygame.image.load('assets/ground.png')

# all sprite
all_sprites = pygame.sprite.Group()

# initializing surfaces
dungeonSurf = pygame.Surface((1024, 1024))

NOITEM = {
    "type": "noitem",
    "patt": 3,
    "matt": 3,
    "defense": 3,
    "vit": 3
}

SWORD = {
    "type": "sword",
    "patt": 12,
    "matt": 4,
    "defense": 9,
    "vit": 5
}

WAND = {
    "type": "wand",
    "patt": 3,
    "matt": 12,
    "defense": 6,
    "vit": 9
}

LANCE = {
    "type": "lance",
    "patt": 9,
    "matt": 3,
    "defense": 12,
    "vit": 6
}

TOME = {
    "type": "tome",
    "patt": 1,
    "matt": 16,
    "defense": 7,
    "vit": 6
}

ALLITEM = [SWORD, WAND, LANCE, TOME]


# dungeon generation class
class DungeonGen:
    def __init__(self, x, y, width, height, depth, master=None):
        # defining variables
        self.generated = 0
        self.bossgenerated = 0
        # BSP start coordinate
        self.chests = []
        self.enemies = []
        self.chestID = 0
        self.enemiesID = 0
        self.x = x
        self.y = y
        # BSP leaves size
        self.width = width
        self.height = height
        # recursion count
        self.depth = depth
        # collision detection lists
        self.room = []
        self.path = []
        self.stair = Stair(0, 0)
        self.floor = 0

    def generatedungeon(self):
        # initializing the creation of a BSP tree
        self.bsp = tcod.bsp.BSP(x=self.x, y=self.y, width=self.width, height=self.height)
        self.bsp.split_recursive(
            depth=self.depth,
            min_width=192,
            min_height=192,
            max_vertical_ratio=1,
            max_horizontal_ratio=1,
        )
        # draw dungeon onto surface
        self.killsprites()
        self.chests = []
        self.enemies = []
        self.chestID = 0
        self.enemiesID = 0
        self.room = []
        self.path = []
        self.stair = Stair(0, 0)
        self.generated = 0
        self.blitdungeon()
        self.floor += 1

    def blitdungeon(self):
        # re-emptying the collision lists
        self.room = []
        self.path = []
        count = 0

        # fill dungeonsurf with black
        dungeonSurf.fill((0, 0, 0))

        # fill dungeonsurf with walls
        for x, y in itertools.product(range(0, 1024, BRICK_WIDTH), range(0, 1024, BRICK_HEIGHT)):
            dungeonSurf.blit(wallbg, (x, y))

        for node in self.bsp.pre_order():
            if node.children:
                node1, node2 = node.children
                node132x = node1.x // 32 * 32
                node132y = node1.y // 32 * 32
                node232x = node2.x // 32 * 32
                node232y = node2.y // 32 * 32
                # print('Connect the rooms:\n%s\n%s' % (node1, node2))
                # screen.blit(wall, (node1.x, node1.y))
                # screen.blit(wall, (node2.x, node2.y))
                self.path.append(pygame.draw.line(dungeonSurf, (0, 255, 0), (node132x + 15, node132y + 15),
                                                  (node232x + 15, node232y + 15), 32))
            else:
                node32x = node.x // 32 * 32
                node32y = node.y // 32 * 32
                roomX = node32x - (3 * 32)
                roomY = node32y - (3 * 32)
                node32width = node.width * 0.7 // 32 * 32
                node32height = node.height * 0.7 // 32 * 32
                # print('Dig a room for %s.' % node)

                self.room.append(pygame.draw.rect(dungeonSurf, (255, 0, 0), (roomX, roomY, node32width, node32height)))
                for x, y in itertools.product(range(roomX, roomX + int(node32width), BRICK_WIDTH),
                                              range(roomY, roomY + int(node32height), BRICK_HEIGHT)):
                    dungeonSurf.blit(floorbg, (x, y))

                # chest generation
                if self.generated == 0:
                    if random.randint(0, 4) == 4:
                        self.chests.append(Chest(random.randint(roomX, roomX + node32width),
                                                 random.randint(roomY, roomY + node32height), self.chestID))
                        self.chestID += 1

                    if random.randint(0, 2) == 2:
                        self.enemies.append(Enemy(random.randint(roomX, roomX + node32width),
                                                  random.randint(roomY, roomY + node32height), self.enemiesID))
                        self.enemies.append(Enemy(random.randint(roomX, roomX + node32width),
                                                  random.randint(roomY, roomY + node32height), self.enemiesID))
                        self.enemiesID += 1
                    count += 1
                    if count == 6:
                        self.stair = Stair(random.randint(self.room[-1].x, self.room[-1].x + node32width),
                                                random.randint(self.room[-1].y, self.room[-1].y + node32height))

                for i in range(len(self.chests)):
                    all_sprites.add(self.chests[i])
                for i in range(len(self.enemies)):
                    all_sprites.add(self.enemies[i])
                all_sprites.add(self.stair)

                screen.blit(floor, (node32x, node32y))
                screen.blit(dungeonSurf, (0, 0))

        self.generated = 1
        return None

    def killsprites(self):
        for i in range(len(self.chests)):
            self.chests[i].kill()
        for i in range(len(self.enemies)):
            self.enemies[i].kill()
        self.stair.kill()

    def readmap(self):
        if self.bossgenerated == 0:
            self.room = []
            self.room.append(pygame.draw.rect(dungeonSurf, (255, 0, 0), (64, 64, 896, 896)))
            for x, y in itertools.product(range(64, 960, BRICK_WIDTH),
                                          range(64, 960, BRICK_HEIGHT)):
                dungeonSurf.blit(floorbg, (x, y))
            self.killsprites()
            self.enemies = []
            self.enemies.append(Enemy(384, 384, 900))
            for i in range(len(self.enemies)):
                all_sprites.add(self.enemies[i])
        screen.blit(dungeonSurf, (0, 0))
        self.bossgenerated = 1
    def readmapregen(self):
        self.room = []
        self.room.append(pygame.draw.rect(dungeonSurf, (255, 0, 0), (64, 64, 896, 896)))
        for x, y in itertools.product(range(64, 960, BRICK_WIDTH),
                                      range(64, 960, BRICK_HEIGHT)):
            dungeonSurf.blit(floorbg, (x, y))


# player sprite class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('plr1.png')
        self.rect = self.image.get_rect()
        self.rect.x = 128
        self.rect.y = 128
        self.rotation = 0
        self.prevpos = [0, 0]
        self.collide = []
        self.currentitem = Item()
        self.currentitem.generate(ALLITEM[random.randint(0, len(ALLITEM) - 1)])
        self.level = 1
        self.maxhp = 50
        self.hp = 50
        self.patt = 10
        self.matt = 10
        self.defense = 10

        self.updatestats()

    def moveup(self):
        self.image = pygame.transform.rotate(self.image, self.rotation + 180)
        self.rotation = 180
        self.prevpos[0] = self.rect.x
        self.prevpos[1] = self.rect.y
        self.rect.y -= 32
        self.resolvecollision()
        self.currentitem.use()
        return None

    def moveleft(self):
        self.image = pygame.transform.rotate(self.image, self.rotation + 270)
        self.rotation = 90
        self.prevpos[0] = self.rect.x
        self.prevpos[1] = self.rect.y
        self.rect.x -= 32
        self.resolvecollision()
        self.currentitem.use()
        return None

    def movedown(self):
        self.image = pygame.transform.rotate(self.image, self.rotation + 0)
        self.rotation = 0
        self.prevpos[0] = self.rect.x
        self.prevpos[1] = self.rect.y
        self.rect.y += 32
        self.resolvecollision()
        self.currentitem.use()
        return None

    def moveright(self):
        self.image = pygame.transform.rotate(self.image, self.rotation + 90)
        self.rotation = 270
        self.prevpos[0] = self.rect.x
        self.prevpos[1] = self.rect.y
        self.rect.x += 32
        self.resolvecollision()
        self.currentitem.use()
        return None

    def resolvecollision(self):
        self.collide = []
        for i in range(len(newdungeon.room)):
            self.collide.append(self.rect.colliderect(newdungeon.room[i]))
            # print(f'Room {i}: {collide}')
        for i in range(len(newdungeon.path)):
            self.collide.append(self.rect.colliderect(newdungeon.path[i]))
            # print(f'Path {i}: {collide}')
        if 1 not in self.collide:
            self.rect.x = self.prevpos[0]
            self.rect.y = self.prevpos[1]
            return True
        return False

    def getitem(self):
        self.currentitem.generate(ALLITEM[random.randint(0, len(ALLITEM) - 1)])
        print(f'type: {self.currentitem.type} '
              f'patt: {self.currentitem.patt} '
              f'matt: {self.currentitem.matt} '
              f'def: {self.currentitem.defense} '
              f'vit: {self.currentitem.vit}')
        self.updatestats()

    def updatestats(self):
        self.hp = 50 * int(self.currentitem.vit * (1 + (0.4 * newdungeon.floor)))
        self.maxhp = self.hp
        self.patt = 10 * int(self.currentitem.patt * (1 + (0.4 * newdungeon.floor)))
        self.matt = 10 * int(self.currentitem.matt * (1 + (0.4 * newdungeon.floor)))
        self.defense = 10 * int(self.currentitem.defense * (1 + (0.4 * newdungeon.floor)))

    def hpbar(self):
        hprect = pygame.draw.rect(screen, (255, 0, 0), (32, 16, int(192 * (self.hp / self.maxhp)), 16))
        hptext = myfont.render(f'HP: {self.hp}/{self.maxhp}', False, (255, 255, 255))
        pattext = myfont.render(f'PATT: {self.patt}', False, (255, 255, 255))
        mattext = myfont.render(f'MATT: {self.matt}', False, (255, 255, 255))
        defensetext = myfont.render(f'DEF: {self.defense}', False, (255, 255, 255))

        screen.blit(hptext, (32, 12))
        screen.blit(defensetext, (128, 12))
        screen.blit(pattext, (32, 32))
        screen.blit(mattext, (128, 32))


        pygame.display.update()


class Item(pygame.sprite.Sprite):
    def __init__(self, master=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/weapon/sword.png')
        self.rect = self.image.get_rect()
        self.rotation = 0
        self.floor = []
        self.type = ''
        self.patt = 0
        self.matt = 0
        self.defense = 0
        self.vit = 0
        self.natregen = 0

    def generate(self, item):
        self.type = item['type']
        self.patt = int(item['patt'] * random.uniform(0.8, 1.2))
        self.matt = int(item['matt'] * random.uniform(0.8, 1.2))
        self.defense = int(item['defense'] * random.uniform(0.8, 1.2))
        self.vit = int(item['vit'] * random.uniform(0.8, 1.2))

    def use(self):
        self.image = pygame.image.load(f'assets/weapon/{self.type}.png')
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y
        if 180 - player.rotation == 180 or 180 - player.rotation == 0:
            self.image = pygame.transform.rotate(self.image, player.rotation)
        else:
            self.image = pygame.transform.rotate(self.image, player.rotation - 180)
        if player.rotation == 0:
            self.rect.y += 16
        elif player.rotation == 270:
            self.rect.x += 16
        elif player.rotation == 180:
            self.rect.y -= 16
        elif player.rotation == 90:
            self.rect.x -= 16
        self.natregen += 1
        if self.natregen == 5 and player.hp < player.maxhp:
            player.hp += 25
            print(player.hp)
            self.natregen = 0
        elif self.natregen == 5:
            self.natregen = 0

    def spell(self):
        pass


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemyID, master=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('enemy.png')
        self.rect = self.image.get_rect()
        self.rect.x = x // 32 * 32
        self.rect.y = y // 32 * 32
        self.enemyID = enemyID
        self.rotation = 0
        self.patt = int(random.randint(25, 35) * (1 + (0.5 * newdungeon.floor)))
        self.matt = int(random.randint(25, 35) * (1 + (0.5 * newdungeon.floor)))
        self.defense = int(random.randint(25, 35) * (1 + (0.5 * newdungeon.floor)))
        self.vit = int(random.randint(15, 23) * (1 + (0.5 * newdungeon.floor)))
        self.hp = random.randint(5, 10) * self.vit
        self.prevpos = [0, 0]
        self.collide = []
        if enemyID == 900:
            self.image = pygame.image.load('boss.png')
            self.rect = self.image.get_rect()
            self.vit *= 10
            self.hp = random.randint(5, 10) * self.vit
            self.rect.x = x // 32 * 32
            self.rect.y = y // 32 * 32

    def checkcollision(self):
        if self.rect is not None:
            collide = self.rect.colliderect(player.rect)
            if collide == 1:
                print("enemy hit!")
                self.hp -= int((player.patt + player.matt) / (100 + self.defense) * 100)
                player.hp -= int((self.patt + self.matt) / (100 + self.defense) * 100)
                print(f'enemy current hp: {self.hp}')
                print(f'self current hp: {player.hp}')
                # self.kill()
                # self.rect.x *= 32
                self.rect.x = self.prevpos[0]
                self.rect.y = self.prevpos[1]
                player.rect.x = player.prevpos[0]
                player.rect.y = player.prevpos[1]
                if self.hp < 0:
                    self.kill()
                    self.rect.x *= 32

    def move(self):
        if self.rect is not None:
            self.prevpos[0] = self.rect.x
            self.prevpos[1] = self.rect.y
            self.collide = []
            plrcollide = []
            for i in range(len(newdungeon.room)):
                self.collide.append(self.rect.colliderect(newdungeon.room[i]))
            for i in range(len(newdungeon.room)):
                plrcollide.append(player.rect.colliderect(newdungeon.room[i]))
            if self.collide == plrcollide:
                # print("hey im in the same room!, moving to your local area...")
                for i in range(2):
                    if player.rect.x < self.rect.x:
                        self.rect.x -= 32
                        self.image = pygame.transform.rotate(self.image, self.rotation + 270)
                        self.rotation = 90
                    elif player.rect.x > self.rect.x:
                        self.rect.x += 32
                        self.image = pygame.transform.rotate(self.image, self.rotation + 90)
                        self.rotation = 270
                    elif player.rect.y < self.rect.y:
                        self.rect.y -= 32
                        self.image = pygame.transform.rotate(self.image, self.rotation + 180)
                        self.rotation = 180
                    elif player.rect.y > self.rect.y:
                        self.rect.y += 32
                        self.image = pygame.transform.rotate(self.image, self.rotation + 0)
                        self.rotation = 0
            else:
                # print("please come to my room tonight!")
                direction = random.randint(0, 3)
                if direction == 0:
                    self.rect.y += 32
                    self.image = pygame.transform.rotate(self.image, self.rotation + 0)
                    self.rotation = 0
                elif direction == 1:
                    self.rect.x += 32
                    self.image = pygame.transform.rotate(self.image, self.rotation + 90)
                    self.rotation = 270
                elif direction == 2:
                    self.rect.y -= 32
                    self.image = pygame.transform.rotate(self.image, self.rotation + 180)
                    self.rotation = 180
                elif direction == 3:
                    self.rect.x -= 32
                    self.image = pygame.transform.rotate(self.image, self.rotation + 270)
                    self.rotation = 90
            # print(self.collide)
            # print(plrcollide)
            self.resolvecollision()
            if self.enemyID == 900:
                self.rect.x = self.prevpos[0]
                self.rect.y = self.prevpos[1]

    def resolvecollision(self):
        collide = []
        for i in range(len(newdungeon.room)):
            collide.append(self.rect.colliderect(newdungeon.room[i]))
            # print(f'Room {i}: {collide}')
        for i in range(len(newdungeon.path)):
            collide.append(self.rect.colliderect(newdungeon.path[i]))
            # print(f'Path {i}: {collide}')
        if 1 not in collide:
            self.rect.x = self.prevpos[0]
            self.rect.y = self.prevpos[1]
            return True
        return False

    def dungeonaoe(self):
        if step == 0:
            self.hitbox = []
            attack = tcod.bsp.BSP(x=192, y=192, width=832, height=832)
            attack.split_recursive(
                depth=3,
                min_width=192,
                min_height=192,
                max_vertical_ratio=1,
                max_horizontal_ratio=1,
            )
            for node in attack.pre_order():
                if node.children:
                    pass
                else:
                    node32x = node.x // 32 * 32
                    node32y = node.y // 32 * 32
                    roomX = node32x - (3 * 32)
                    roomY = node32y - (3 * 32)
                    node32width = node.width * 0.7 // 32 * 32
                    node32height = node.height * 0.7 // 32 * 32
                    self.hitbox.append(pygame.draw.rect(dungeonSurf, (255, 0, 0), (roomX, roomY, node32width, node32height)))
                    for x, y in itertools.product(range(roomX, roomX + int(node32width), BRICK_WIDTH),
                                                  range(roomY, roomY + int(node32height), BRICK_HEIGHT)):
                        dungeonSurf.blit(wall, (x, y))
        if step >= 3:
            collide = []
            for i in range(len(self.hitbox)):
                collide.append(player.rect.colliderect(self.hitbox[i]))
            if 1 in collide:
                player.hp = int(player.hp * 0.8)
            newdungeon.readmapregen()
            return False
        return True


class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y, chestID):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/chest.png')
        self.rect = self.image.get_rect()
        self.rect.x = x // 32 * 32
        self.rect.y = y // 32 * 32
        self.chestID = chestID

    def checkcollision(self, chest):
        if chest.rect.colliderect(player):
            player.getitem()
            chest.kill()
            self.rect.x *= 32


class Stair(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/staircase.png')
        self.rect = self.image.get_rect()
        self.rect.x = x // 32 * 32
        self.rect.y = y // 32 * 32
        self.level = 0

    def moveup(self):
        if self.rect.colliderect(player):
            self.kill()
            self.level += 1
            newdungeon.generatedungeon()
            player.rect.x = 128
            player.rect.y = 128


# initialization of a new dungeon

newdungeon = DungeonGen(192, 192, 832, 832, 3)
newdungeon.generatedungeon()

player = Player()
all_sprites.add(player)
all_sprites.add(player.currentitem)
atking = False
step = 0

# main loop
running = True
while running:
    clock.tick(20)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if event.key == pygame.locals.K_c:
                print(f'HP: {player.hp}\nPATT: {player.patt}\nMATT: {player.matt}\nDEF: {player.defense}')
                if newdungeon.floor == 5:
                    if not atking:
                        atk = random.randint(1, 3)
                        step = 0
                    if atk == 3:
                        atking = True
                        atking = newdungeon.enemies[0].dungeonaoe()
                        print(step)
                        step += 1
            if event.key == pygame.locals.K_h:
                newdungeon.killsprites()
                newdungeon.generatedungeon()
                print("success")
            if event.key == pygame.locals.K_u:
                newdungeon.blitdungeon()
                all_sprites.draw(screen)
                all_sprites.update()
                pygame.display.update()
                print("updated")
            if event.key == K_UP:
                player.moveup()
                for i in range(len(newdungeon.enemies)):
                    newdungeon.enemies[i].move()
            if event.key == K_DOWN:
                player.movedown()
                for i in range(len(newdungeon.enemies)):
                    newdungeon.enemies[i].move()
            if event.key == K_LEFT:
                player.moveleft()
                for i in range(len(newdungeon.enemies)):
                    newdungeon.enemies[i].move()
            if event.key == K_RIGHT:
                player.moveright()
                for i in range(len(newdungeon.enemies)):
                    newdungeon.enemies[i].move()
            if newdungeon.floor == 5:
                if not atking:
                    atk = random.randint(2, 3)
                    step = 0
                if atk == 3:
                    atking = True
                    atking = newdungeon.enemies[0].dungeonaoe()
                    print(step)
                    step += 1
            else:
                step = 1
        elif event.type == QUIT:
            running = False
    if newdungeon.floor == 5:
        newdungeon.readmap()
    else:
        newdungeon.blitdungeon()
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.update()
    newdungeon.stair.moveup()
    player.hpbar()
    for i in range(len(newdungeon.chests)):
        newdungeon.chests[i].checkcollision(newdungeon.chests[i])
    for ii in range(len(newdungeon.enemies)):
        newdungeon.enemies[ii].checkcollision()

