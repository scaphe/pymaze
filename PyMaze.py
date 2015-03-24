# Maze written using pygame

import sys, pygame, time

S_init=-1
S_none=0
S_right=1
S_left=2
S_up=3
S_down=4


class Sprite():
    def __init__(self, filename, xpos=2, ypos=2, xoff=0, yoff=0):
        self.img = pygame.image.load(filename).convert_alpha()
        self.rect = self.img.get_rect()
        self.xpos = xpos
        self.ypos = ypos
        self.xoff = xoff
        self.yoff = yoff
        self.initxoff = xoff
        self.inityoff = yoff
        print(self.rect)

    def draw(self, screen):
        self.drawAt(screen, self.xpos, self.ypos)

    def drawAt(self, screen, x, y):
        screen.blit(self.img, self.rect.move(x*100+self.xoff, y*80+self.yoff))


class Player():
    def __init__(self, sprite, xpos, ypos):
        self.sprite = sprite
        self.xpos = xpos
        self.ypos = ypos
        self.xoff = 0
        self.yoff = 0
        self.action = S_none

    def animate(self, screen):
        if self.action == S_right: self.xoff += 5
        elif self.action == S_left: self.xoff -= 5
        elif self.action == S_up: self.yoff -= 4
        elif self.action == S_down: self.yoff += 4
        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.sprite.img,
                    self.sprite.rect.move(self.xpos*100+self.xoff, self.ypos*80+self.yoff-40))

    def move(self):
        if self.action == S_right: self.xpos += 1
        elif self.action == S_left: self.xpos -= 1
        elif self.action == S_up: self.ypos -= 1
        elif self.action == S_down: self.ypos += 1
        self.action = S_none
        self.xoff = 0
        self.yoff = 0
        


def drawBackground(screen):
    screen.fill(black)
    for x in range(0, 10):
        for y in range(0, 8):
            dirt.drawAt(screen, x, y)

print("Got here")
try:
    pygame.init()
    size = width, height = 1024, 800
    screen = pygame.display.set_mode(size)

    black = 255, 255, 0
    dirt = Sprite("images/Dirt block.png")
    girlPrincess = Player(Sprite("images/Character Princess Girl.png"), 1, 1)
    boy = Player(Sprite("images/Character Boy.png"), 1, 3)

    drawBackground(screen)

    pygame.display.flip()
    move=S_init
    while 1:
        if move != S_none:
            girlPrincess.action = move
            boy.action = move
            
            for aniStep in range(0,20):
                girlPrincess.animate(screen)
                boy.animate(screen)
                #drawBackground(screen)
                pygame.display.flip()
                time.sleep(0.01)
            
            girlPrincess.move()
            boy.move()
            drawBackground(screen)
            girlPrincess.draw(screen)
            move = S_none

        elif move == S_none:
            for event in pygame.event.get():
                et = event.type
                if et == pygame.QUIT or (et == pygame.KEYDOWN and event.key == pygame.K_q): sys.exit()
                if et == pygame.KEYDOWN:
                    k = event.key
                    if k == pygame.K_x: move=S_right
                    elif k == pygame.K_z: move=S_left
                    elif k == pygame.K_k: move=S_up
                    elif k == pygame.K_m: move=S_down

finally:
    pygame.quit()
    print("Exit")
    
