import sys, pygame, time


class Sprite():
    def __init__(self, filename, xpos=2, ypos=2, xoff=0, yoff=0):
        self.filename = filename
        self.img = pygame.image.load(filename).convert_alpha()
        self.rect = self.img.get_rect()
        self.xpos = xpos
        self.ypos = ypos
        self.xoff = xoff
        self.yoff = yoff
        self.w = self.rect.width
        self.h = self.rect.height
        self.initxoff = xoff
        self.inityoff = yoff

    def draw(self, screen):
        self.drawAt(screen, self.xpos, self.ypos)

    def drawAt(self, screen, x, y):
        screen.blit(self.img, self.rect.move(x*100+self.xoff, y*80+self.yoff))


class Backgrounds:
    def __init__(self, backgroundMapFile):
        self.map = {}
        for aline in open(backgroundMapFile):
            line = aline.rstrip()
            if line != '':
                tileId = line[0]
                self.map[tileId] = Sprite(line[2:])
                #print("Set tileId '"+str(tileId)+"' is",self.map[tileId].filename)



def drawBackground(screen, backgrounds, room):
    black = 255, 255, 0
    screen.fill(black)
    for x in range(0, 9):
        for y in range(0, 8):
            tile = room.tiles[x][y]
            if tile != ' ':
                bg = backgrounds.map[tile]
                bg.drawAt(screen, x, y)

