import sys, pygame, time


# Immutable (nice callers respecting my underscores) position
class Pos:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __str__(self): return "Pos("+str(self._x)+", "+str(self._y)+")"

    def x(self): return self._x
    def y(self): return self._y

    # Returns a changed copy
    def plus(self, other):
        return Pos(self._x + other._x, self._y + other._y)

    def equals(self, other):
        if self._x == other._x and self._y == other._y: return True
        else: return False

    def isEmpty(self): return self._x == 0 and self._y == 0


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


# Keep track of wanting to draw a sprite at a place on the screen
class DrawTask:
    def __init__(self, sprite, x, y):
        self.sprite = sprite
        self.x = x
        self.y = y

    def apply(self, screen):
        screen.blit(self.sprite.img, self.sprite.rect.move(self.x, self.y))


# Keep track of wanting to undraw a rectangle on the screen
class UndrawTask:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def apply(self, screen, bgScreen):
        try:
            bgImg = bgScreen.subsurface(pygame.Rect(self.x, self.y, self.w, self.h))
            screen.blit(bgImg, pygame.Rect(self.x, self.y, bgImg.get_rect().width, bgImg.get_rect().height))
        except ValueError as e:
            print('Failed with',e,'with',self.x,self.y,self.w,self.h)
        

# Keep track of what redraws we want to do, apply() will actually draw them (in the right order)
class RedrawsRequired:
    def __init__(self):
        self.reset()

    def reset(self):
        self.bgRedraws = []
        self.fgRedraws = []

    def addFg(self, task):
        self.fgRedraws.append(task)

    def addBg(self, task):
        self.bgRedraws.append(task)

    def apply(self, screen, bgScreen):
        for x in self.bgRedraws: x.apply(screen, bgScreen)
        for x in self.fgRedraws: x.apply(screen)
        self.reset()
        


def drawBackground(screen, backgrounds, room):
    black = 0, 0, 0
    screen.fill(black)
    for x in range(0, 9):
        for y in range(0, 8):
            tile = room.tiles[x][y]
            if tile != ' ':
                bg = backgrounds.map[tile]
                bg.drawAt(screen, x, y)

